<script lang="ts">
  import { onMount } from 'svelte';
  import type { PageData } from './$types';
  import * as Table from "$lib/components/ui/table";
  import * as Sheet from "$lib/components/ui/sheet";
  import { Button } from "$lib/components/ui/button/index.js";
  import * as Pagination from "$lib/components/ui/pagination";
  import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
  import { goto } from '$app/navigation';
  import { isLoggedIn, userName, logout, checkAuth } from '../stores/auth';

  const API_URL = 'http://localhost:5000';

  interface Job {
      job_id: number;
      business_title: string;
      agency: string;
      work_location: string;
      job_description: string;
      salary_range_from: string;
      salary_range_to: string;
      preferred_skills: string;
      additional_information: string;
  }

  let savedJobs: Job[] = [];
  let isLoading = true;
  let error: string | null = null;
  let selectedJob: Job | null = null;
  let currentPage = 1;
  const perPage = 10;
  let applications: Record<number, boolean> = {};


  $: paginatedJobs = savedJobs.slice((currentPage - 1) * perPage, currentPage * perPage);
  $: totalJobs = savedJobs.length;

  onMount(async () => {
      if (!checkAuth()) {
          goto('/auth');
      } else {
          await fetchSavedJobs();
      }
  });

  async function fetchSavedJobs() {
      isLoading = true;
      error = null;
      try {
          const userData = JSON.parse(localStorage.getItem('userData') || '{}');
          if (!userData.user_id) {
              throw new Error('User ID not found in local storage');
          }

          const response = await fetch(`${API_URL}/get_saved_jobs`, {
              method: 'GET',
              headers: {
                  'Content-Type': 'application/json',
                  'User-Id': userData.user_id
              },
          });

          if (response.ok) {
              const data = await response.json();
              savedJobs = data.savedJobs;
          } else {
              const errorData = await response.json();
              throw new Error(errorData.error || 'Failed to fetch saved jobs');
          }
      } catch (err) {
          console.error('Error fetching saved jobs:', err);
          error = err.message;
      } finally {
          isLoading = false;
      }
  }

  function goBack() {
      goto('/jobs');
  }

  async function unsaveJob(jobId: number) {
      if (!checkAuth()) {
          console.error('User not logged in');
          goto('/auth');
          return;
      }

      try {
          const userData = JSON.parse(localStorage.getItem('userData') || '{}');
          if (!userData.user_id) {
              throw new Error('User ID not found in local storage');
          }

          const response = await fetch(`${API_URL}/unsave_job/${jobId}`, {
              method: 'DELETE',
              headers: {
                  'Content-Type': 'application/json',
                  'User-Id': userData.user_id
              },
          });

          if (response.ok) {
              const result = await response.json();
              console.log(result.message);
              savedJobs = savedJobs.filter(job => job.job_id !== jobId);
          } else {
              const errorData = await response.json();
              throw new Error(errorData.error || 'Failed to unsave job');
          }
      } catch (err) {
          console.error('Error unsaving job:', err);
          error = err.message;
      }
  }

  function openSheet(job: Job) {
      selectedJob = job;
      (document.querySelector('#jobSheetTrigger') as HTMLButtonElement)?.click();
  }

  function handlePageChange(newPage: number) {
      currentPage = newPage;
  }

  async function applyToJob(jobId: number) {
  if (!checkAuth()) {
    console.error('User not logged in');
    goto('/auth');
    return;
  }

  try {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    if (!userData.user_id) {
      throw new Error('User ID not found in local storage');
    }

    const response = await fetch(`${API_URL}/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Id': userData.user_id
      },
      body: JSON.stringify({ job_id: jobId }),
    });

    if (response.ok) {
      const result = await response.json();
      console.log(result.message);
      applications[jobId] = true;
      applications = { ...applications };
    } else {
      const errorData = await response.json();
      console.error('Failed to apply for job:', errorData.error);
    }
  } catch (error) {
    console.error('Error applying for job:', error);
  }
}

  function handleLogout() {
      logout();
      goto('/auth');
  }
</script>

<nav class="border-b-2 border-black">
  <div class="container mx-auto flex items-stretch h-16">
    <div class="flex items-center pr-4 border-r-2 border-black h-full">
      <div class="text-black font-bold  hero-text">Job Portal</div>
    </div>
    {#if $isLoggedIn}
      <div class="flex items-center space-x-4 pl-20 ml-auto ">
        <a href="/applicant-profile" class="text-black hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium">Update Profile</a>
        <a href="/jobs" class="text-black hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium">Job Postings</a>
        <a href="/applied-jobs" class="text-black hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium">Applied Jobs</a>
        <a href="/SavedJobs" class="text-black hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium">Saved Postings</a>
        <span class="text-black text-sm">Welcome, {$userName}!</span>
        <Button variant="outline" size="sm" on:click={handleLogout}>Logout</Button>
      </div>
    {:else}
      <Button on:click={() => goto('/auth')}>Login</Button>
    {/if}
  </div>
</nav>

<main class="container ">
  <h1 class="text-3xl font-bold mb-6" >Saved Job Postings</h1>

  Here you can see all of your saved Job postings
  <br>
  
  {#if $isLoggedIn}
    

      {#if isLoading}
          <p>Loading saved jobs...</p>
      {:else if error}
          <p class="error">Error: {error}</p>
      {:else if paginatedJobs && paginatedJobs.length > 0}
          <Table.Root>
              <Table.Caption>Saved Job Postings</Table.Caption>
              <Table.Header>
                  <Table.Row>
                      <Table.Head class="w-[100px]">ID</Table.Head>
                      <Table.Head>Title</Table.Head>
                      <Table.Head>Company</Table.Head>
                      <Table.Head>Location</Table.Head>
                      <Table.Head>More information</Table.Head>
                      <Table.Head>Actions</Table.Head>
                  </Table.Row>
              </Table.Header>
              <Table.Body>
                  {#each paginatedJobs as job}
                      <Table.Row>
                          <Table.Cell class="font-medium">{job.job_id}</Table.Cell>
                          <Table.Cell>{job.business_title}</Table.Cell>
                          <Table.Cell>{job.agency}</Table.Cell>
                          <Table.Cell>{job.work_location}</Table.Cell>
                          <Table.Cell>
                              <Button on:click={() => openSheet(job)}>See More</Button>
                          </Table.Cell>
                          <Table.Cell>
                              <Button on:click={() => unsaveJob(job.job_id)}>Unsave</Button>
                              <Button  variant="outline" on:click={() => applyToJob(job.job_id)}>Apply</Button>

                          </Table.Cell>
                      </Table.Row>
                  {/each}
              </Table.Body>
          </Table.Root>
      {:else}
          <p>No saved job postings available at the moment.</p>
      {/if}

      <Sheet.Root>
          <Sheet.Trigger id="jobSheetTrigger" style="display: none;">Open</Sheet.Trigger>
          <Sheet.Content>
              <Sheet.Header>
                  <Sheet.Title>{selectedJob?.business_title}</Sheet.Title>
                  <ScrollArea class="h-[850px] w-[360px] rounded-md p-4">
                      <Sheet.Description>
                          <p><strong>ID:</strong> {selectedJob?.job_id}</p>
                          <br>
                          <p><strong>Company:</strong> {selectedJob?.work_location}</p>
                          <br>
                          <p><strong>Title:</strong> {selectedJob?.business_title}</p>
                          <br>
                          <p><strong>Description:</strong> {selectedJob?.job_description}</p>
                          <br>
                          <p><strong>Salary range:</strong> {selectedJob?.salary_range_from} - {selectedJob?.salary_range_to}</p>
                          <br>
                          <p><strong>Preferred skills:</strong> {selectedJob?.preferred_skills}</p>
                          <br>
                          <p><strong>Additional information:</strong> {selectedJob?.additional_information}</p>
                          <br>
                      </Sheet.Description>
                  </ScrollArea>
              </Sheet.Header>
          </Sheet.Content>
      </Sheet.Root>

      <Pagination.Root count={totalJobs} {perPage} let:pages {currentPage} onPageChange={handlePageChange}>
          <Pagination.Content>
              <Pagination.Item>
                  <Pagination.PrevButton />
              </Pagination.Item>
              {#each pages as page (page.key)}
                  {#if page.type === "ellipsis"}
                      <Pagination.Item>
                          <Pagination.Ellipsis />
                      </Pagination.Item>
                  {:else}
                      <Pagination.Item>
                          <Pagination.Link {page} isActive={currentPage === page.value}>
                              {page.value}
                          </Pagination.Link>
                      </Pagination.Item>
                  {/if}
              {/each}
              <Pagination.Item>
                  <Pagination.NextButton />
              </Pagination.Item>
          </Pagination.Content>
      </Pagination.Root>
  {:else}
      <p>Please log in to view saved job postings.</p>
      <Button on:click={() => goto('/auth')}>Go to Login</Button>
  {/if}
</main>

<style>
  main {
      padding: 1rem;
  }

  h1 {
      font-size: 2rem;
      margin-bottom: 1rem;
  }

  .error {
      color: red;
      font-weight: bold;
  }
</style>