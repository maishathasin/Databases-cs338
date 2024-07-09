<script lang="ts">
  import type { Job } from '../../lib/types';
  import * as Table from "$lib/components/ui/table";
  import * as Sheet from "$lib/components/ui/sheet";
  import { Button } from "$lib/components/ui/button/index.js";
  import * as Pagination from "$lib/components/ui/pagination";
  import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { goto } from '$app/navigation';



  export let data: { jobs?: Job[] } = { jobs: [] };
  let selectedJob: Job | null = null;
  let applications: Record<number, boolean> = {};
  let isLoggedIn = false;
  let searchTerm = '';
  let savedJobs: Record<number, boolean> = {};


  function goToSavedPostings() {
    goto('/SavedJobs');
  }

  //let currentPage = 1;
  const perPage = 10;

  function handlePageChange(newPage: number) {
  currentPage = newPage;
}

  function openSheet(job: Job) {
      selectedJob = job;
      (document.querySelector('#jobSheetTrigger') as HTMLButtonElement)?.click();
  }

  //$: totalJobs = data.jobs?.length || 0;
  $: totalPages = Math.ceil(totalJobs / perPage);
  //$: paginatedJobs = data.jobs || [];


  let currentPage = 1;

  $: filteredJobs = data.jobs?.filter(job => 
    job.business_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.agency.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  $: totalJobs = data.jobs?.length || 0;
  $: paginatedJobs = data.jobs?.slice((currentPage - 1) * perPage, currentPage * perPage) || [];
  const API_URL = 'http://localhost:5000';


  async function searchJobs() {
    try {
      const response = await fetch(`${API_URL}/search_jobs?query=${searchTerm}`);
      if (response.ok) {
        const result = await response.json();
        data.jobs = result.jobs;
        currentPage = 1;
      } else {
        console.error('Failed to search jobs');
      }
    } catch (error) {
      console.error('Error searching jobs:', error);
    }
  }


  async function saveJob(jobId: number) {
    if (!isLoggedIn) {
      console.error('User not logged in');
      // Optionally, redirect to login page or show login modal
      return;
    }

    try {
      const response = await fetch(`${API_URL}/save_job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId }),
        credentials: 'include',
      });
      if (response.ok) {
        savedJobs[jobId] = true;
        savedJobs = { ...savedJobs };
      } else if (response.status === 401) {
        console.error('User not authenticated');
        isLoggedIn = false;
        // Optionally, redirect to login page or show login modal
      } else {
        console.error('Failed to save job');
      }
    } catch (error) {
      console.error('Error saving job:', error);
    }
  }
  async function login(email: string, password: string) {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include',
      });
      if (response.ok) {
        isLoggedIn = true;
        // Optionally, fetch user data or applications here
      } else {
        console.error('Login failed');
      }
    } catch (error) {
      console.error('Error during login:', error);
    }
  }


  async function unsaveJob(jobId: number) {
    try {
      const response = await fetch(`${API_URL}/unsave_job/${jobId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (response.ok) {
        delete savedJobs[jobId];
        savedJobs = { ...savedJobs };
      } else {
        console.error('Failed to unsave job');
      }
    } catch (error) {
      console.error('Error unsaving job:', error);
    }
  }

  async function applyToJob(jobId: number) {
    if (!isLoggedIn) {
      console.error('User not logged in');
      // Optionally, redirect to login page or show login modal
      return;
    }

    try {
      const response = await fetch(`${API_URL}/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId }),
        credentials: 'include',
      });
      if (response.ok) {
        applications[jobId] = true;
        applications = { ...applications };
      } else if (response.status === 401) {
        console.error('User not authenticated');
        isLoggedIn = false;
        // Optionally, redirect to login page or show login modal
      } else {
        console.error('Failed to apply for job');
      }
    } catch (error) {
      console.error('Error applying for job:', error);
    }
  }

  async function deleteApplication(jobId: number) {
    try {
      const response = await fetch(`http://localhost:5000/delete_application/${jobId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        delete applications[jobId];
        applications = { ...applications };
      } else {
        console.error('Failed to delete application');
      }
    } catch (error) {
      console.error('Error deleting application:', error);
    }
  }

  function updateApplication(jobId: number) {
    //implement update functionality
    console.log('Update application for job:', jobId);
  }
  
  </script>

<main>
  <h1>Job Postings</h1>

  <form class="flex w-full max-w-sm items-center space-x-2 mb-4" on:submit|preventDefault={searchJobs}>
    <Input type="text" placeholder="Search jobs..." bind:value={searchTerm} />
    <Button type="submit">Search</Button>
  </form>
  <Button on:click={goToSavedPostings}>See Saved Postings</Button>


  {#if paginatedJobs && paginatedJobs.length > 0}
  <Table.Root>
    <Table.Caption>Job Postings</Table.Caption>
    <Table.Header>
      <Table.Row>
        <Table.Head class="w-[100px]">ID</Table.Head>
        <Table.Head>Title</Table.Head>
        <Table.Head>Companhy</Table.Head>
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
            {#if applications[job.job_id]}
              <Button on:click={() => deleteApplication(job.job_id)}>Delete</Button>
              <Button on:click={() => updateApplication(job.job_id)}>Update</Button>
            {:else}
              <Button on:click={() => applyToJob(job.job_id)}>Apply</Button>
            {/if}
            {#if savedJobs[job.job_id]}
            <Button on:click={() => unsaveJob(job.job_id)}>Unsave</Button>
          {:else}
            <Button on:click={() => saveJob(job.job_id)}>Save</Button>
          {/if}
          </Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>
{:else}
  <p>No job postings available at the moment.</p>
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
          <Pagination.Item >
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
</main>

<style>
  main {
      padding: 1rem;
  }

  h1 {
      font-size: 2rem;
      margin-bottom: 1rem;
  }
</style>