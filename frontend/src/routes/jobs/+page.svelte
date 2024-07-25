<script lang="ts">
  import type { Job } from '../../lib/types';
  import * as Table from "$lib/components/ui/table";
  import * as Sheet from "$lib/components/ui/sheet";
  import { Button } from "$lib/components/ui/button/index.js";
  import * as Pagination from "$lib/components/ui/pagination";
  import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { goto } from '$app/navigation';
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import { Toaster } from "$lib/components/ui/sonner";
  import { toast } from "svelte-sonner";
  import { ModeWatcher } from "mode-watcher";




  import { onMount } from 'svelte';
  import { isLoggedIn, userName, logout, checkAuth } from '../stores/auth';


  export let data: { jobs?: Job[] } = { jobs: [] };
  let selectedJob: Job | null = null;
  let applications: Record<number, boolean> = {};
  let searchTerm = '';
  let savedJobs: Record<number, boolean> = {};
  let isLoading = true;


  function goToSavedPostings() {
    goto('/SavedJobs');
  }

  const API_URL = 'http://localhost:5000';

  onMount(async () => {
    console.log('Jobs page mounted, userName is:', $userName);

  if (!checkAuth()) {
    goto('/auth');
  } else {
    isLoading = true;
    await fetchJobs();
    isLoading = false;
  }
});

  async function fetchJobs() {
  try {
    const response = await fetch(`${API_URL}/jobs`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Add this line to include cookies
    });
    if (response.ok) {
      const jobsData = await response.json();
      data = { jobs: jobsData }; // Ensure we're setting the jobs property
      console.log('Fetched jobs:', data.jobs); // Add this line for debugging
    } else {
      console.error('Failed to fetch jobs');
    }
  } catch (error) {
    console.error('Error fetching jobs:', error);
  }
}




  function handleLogout() {
    logout();
    goto('/auth');
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

    const response = await fetch(`${API_URL}/save_job`, {
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
      savedJobs[jobId] = true;
      savedJobs = { ...savedJobs };
      // Show success toast
      toast.success("Job saved successfully", {
          description: `Job ID: ${jobId} has been added to your saved jobs`,
          action: {
            label: "View Saved Jobs",
            onClick: () => goto('/SavedJobs')
          }});
    } else {
      const errorData = await response.json();
      console.error('Failed to save job:', errorData.error);
    }
  } catch (error) {
    console.error('Error saving job:', error);
  }
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
      delete savedJobs[jobId];
      savedJobs = { ...savedJobs };
    } else {
      const errorData = await response.json();
      console.error('Failed to unsave job:', errorData.error);
    }
  } catch (error) {
    console.error('Error unsaving job:', error);
  }
}

async function applyToJob(jobId: number) {
  if (!checkAuth()) {
    console.error('User not logged in');
    goto('/auth');
    return;
  }

  // Prevent applying if already applied
  if (applications[jobId]) {
    console.log('Already applied to this job');
    toast.error("Application not submitted", {
      description: "You have already applied for this job.",
    });
    return;
  }

  try {
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    if (!userData.user_id) {
      throw new Error('User ID not found in local storage');
    }

    console.log('Applying to job:', jobId); // Log the job being applied to

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
      console.log('Application result:', result.message);
      
      // Update state in a more controlled manner
      applications = { ...applications, [jobId]: true };

      // Show success toast
      toast.success("Application submitted successfully", {
        description: `You've applied for job ID: ${jobId}`,
        action: {
          label: "View Applications",
          onClick: () => goto('/applied-jobs')
        }
      });
    } else {
      const errorData = await response.json();
      console.error('Failed to apply for job:', errorData.error);
      if (errorData.error.includes("already applied")) {
        toast.error("Application not submitted", {
          description: "You have already applied for this job.",
        });
      }
    }
  } catch (error) {
    console.error('Error applying for job:', error);
  }
}

async function deleteApplication(jobId: number) {
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

    const response = await fetch(`${API_URL}/delete_application/${jobId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'User-Id': userData.user_id
      },
    });

    if (response.ok) {
      const result = await response.json();
      console.log(result.message);
      delete applications[jobId];
      applications = { ...applications };
    } else {
      const errorData = await response.json();
      console.error('Failed to delete application:', errorData.error);
    }
  } catch (error) {
    console.error('Error deleting application:', error);
  }
}

  function updateApplication(jobId: number) {
    //implement update functionality
    console.log('Update application for job:', jobId);
  }

  function goToProfile() {
    goto('/applicant-profile');
  }
  function goToApplied() {
    goto('/applied-jobs');
  }



  ///JOb recommendaions 
  interface JobRecommendation {
        job_id: number;
        business_title: string;
        agency: string;
        work_location: string;
        salary_range_from: number;
        salary_range_to: number;
        match_score: number;
    }

    let recommendations: JobRecommendation[] = [];
    let error: string | null = null;

    async function fetchRecommendations() {
        isLoading = true;
        error = null;
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/job_recommendations`, {
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
            });

            if (response.ok) {
                recommendations = await response.json();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch job recommendations');
            }
        } catch (err) {
            console.error('Error fetching job recommendations:', err);
            error = err.message;
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        console.log('Component mounted');
        if (checkAuth()) {
            console.log('User authenticated, fetching recommendations');
            fetchRecommendations();
        } else {
            console.log('User not authenticated');
            goto('/auth');
        }
    });

    function handleRefresh() {
        fetchRecommendations();
    }

  
  </script>
<nav class="border-b-2 border-black">
  <div class="container mx-auto flex items-stretch h-16">
    <div class="flex items-center pr-4 border-r-2 border-black h-full">
      <div class="text-black font-bold text-3xl hero-text">Job Portal</div>
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

<main class="container mx-auto mt-8 flex">
  <!-- Job Listings Column (Left) -->
  <div class="w-3/4 pr-4">
    <h1 class="text-3xl font-bold mb-6">Data Job Postings</h1>

    {#if $isLoggedIn}
      <form class="flex w-full max-w-sm items-center space-x-2 mb-4" on:submit|preventDefault={searchJobs}>
        <Input type="text" placeholder="Search jobs..." bind:value={searchTerm} />
        <Button type="submit">Search</Button>
      </form>

      {#if paginatedJobs && paginatedJobs.length > 0}
        <Table.Root>
          <Table.Caption>Job Postings</Table.Caption>
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
                  {#if applications[job.job_id]}
                    <Button on:click={() => deleteApplication(job.job_id)}>Delete</Button>
                    <Button on:click={() => updateApplication(job.job_id)}>Update</Button>
                  {:else}
                    <Button  variant="outline" on:click={() => applyToJob(job.job_id)}>Apply</Button>
                    <br>
                  {/if}
                  {#if savedJobs[job.job_id]}
                    <Button on:click={() => unsaveJob(job.job_id)}>Unsave</Button>
                  {:else}
                  <br>
                    <Button  variant="secondary" on:click={() => saveJob(job.job_id)}>Save</Button>
                  {/if}
                </Table.Cell>
              </Table.Row>
            {/each}
          </Table.Body>
        </Table.Root>
      {:else}
        <p>No job postings available at the moment.</p>
      {/if}

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
      {:else}
      <p>Please log in to view job postings.</p>
      <Button on:click={() => goto('/auth')}>Go to Login</Button>
    {/if}
  </div>
    <!-- Sheet and Pagination components remain unchanged -->
  <!-- Recommendations Column (Right) -->
  <div class="w-1/4 pl-4 border-l-2 border-gray-200">
    <div class="sticky top-4">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">Job Recommendations</h2>
        <Button size="sm" on:click={handleRefresh}>Refresh</Button>
      </div>

      <ScrollArea class="h-[calc(100vh-200px)]">
        {#if isLoading}
          <p class="text-center text-gray-600">Loading recommendations...</p>
        {:else if error}
          <p class="error text-center text-red-500">Error: {error}</p>
        {:else if recommendations.length > 0}
          <div class="space-y-4">
            {#each recommendations as job}
              <Card>
                <CardHeader>
                  <CardTitle>{job.business_title}</CardTitle>
                  <CardDescription>{job.agency}</CardDescription>
                </CardHeader>
                <CardContent>
                  <p class="mb-2"><strong>Location:</strong> {job.work_location}</p>
                  <p class="mb-2"><strong>Salary:</strong> ${job.salary_range_from} - ${job.salary_range_to}</p>
                  <Badge variant="secondary">
                    Match: {job.match_score !== undefined ? (job.match_score * 100).toFixed(2) + '%' : 'N/A'}
                  </Badge>
                </CardContent>
                <CardFooter class="flex justify-between">
                  <Button variant="outline" size="sm" on:click={() => applyToJob(job.job_id)}>Apply</Button>
                  <Button variant="secondary" size="sm" on:click={() => saveJob(job.job_id)}>Save</Button>

                </CardFooter>
              </Card>
            {/each}
          </div>
        {:else}
          <p class="text-center text-gray-600">No recommendations available at this time.</p>
        {/if}
      </ScrollArea>
    </div>
  </div>
  <ModeWatcher defaultMode={"light"} />

  <Toaster />

</main>
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
<style>

 

  main {
      padding: 1rem;
 }

  h1 {
      font-size: 2rem;
      margin-bottom: 1rem;
  }
  .hero-text {
    font-size: 5rem;
    font-weight: bold;
    text-align: left;
    margin-top: 0.5rem;
    margin-left: 0;
    color: black;
    background-color: transparent !important;
    font-family: 'Terminal Grotesque', sans-serif; /* Add fallback font */
  } 
  :global(body) {
    background-color: white;
    color: #0a0a0a;
  }

</style>