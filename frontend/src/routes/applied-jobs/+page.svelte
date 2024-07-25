<script lang="ts">
    import type { Job } from '../../lib/types';
    import * as Table from "$lib/components/ui/table";
    import * as Sheet from "$lib/components/ui/sheet";
    import { Button } from "$lib/components/ui/button/index.js";
    import * as Pagination from "$lib/components/ui/pagination";
    import { ScrollArea } from "$lib/components/ui/scroll-area/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { isLoggedIn, userName, logout, checkAuth } from '../stores/auth';

    interface AppliedJob extends Job {
        application_id: number;
        application_date: string;
        status: string;
    }

    let appliedJobs: AppliedJob[] = [];
    let selectedJob: AppliedJob | null = null;
    let searchTerm = '';
    let isLoading = true;

    const API_URL = 'http://localhost:5000';
    const perPage = 10;
    let currentPage = 1;

    $: filteredJobs = appliedJobs.filter(job => 
        job.business_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.agency.toLowerCase().includes(searchTerm.toLowerCase())
    );

    $: totalJobs = filteredJobs.length;
    $: paginatedJobs = filteredJobs.slice((currentPage - 1) * perPage, currentPage * perPage);

    onMount(async () => {
        console.log('Applied Jobs page mounted, userName is:', $userName);
        if (!checkAuth()) {
            goto('/auth');
        } else {
            isLoading = true;
            await fetchAppliedJobs();
            isLoading = false;
        }
    });

    async function fetchAppliedJobs() {
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/applied_jobs`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
            });
            if (response.ok) {
                appliedJobs = await response.json();
                console.log('Fetched applied jobs:', appliedJobs);
            } else {
                console.error('Failed to fetch applied jobs');
            }
        } catch (error) {
            console.error('Error fetching applied jobs:', error);
        }
    }

    function handleLogout() {
        logout();
        goto('/auth');
    }

    function handlePageChange(newPage: number) {
        currentPage = newPage;
    }

    function openSheet(job: AppliedJob) {
        selectedJob = job;
        (document.querySelector('#jobSheetTrigger') as HTMLButtonElement)?.click();
    }

    async function deleteApplication(applicationId: number) {
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

            const response = await fetch(`${API_URL}/delete_application/${applicationId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result.message);
                appliedJobs = appliedJobs.filter(job => job.application_id !== applicationId);
            } else {
                const errorData = await response.json();
                console.error('Failed to delete application:', errorData.error);
            }
        } catch (error) {
            console.error('Error deleting application:', error);
        }
    }

    function goToAllJobs() {
        goto('/jobs');
    }
</script>

<nav class="border-b-2 border-black">
    <div class="container mx-auto flex items-stretch h-16">
      <div class="flex items-center pr-4 border-r-2 border-black h-full">
        <div class="text-black font-bold hero-text">Job Portal</div>
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
  
<main class="container">
    <h1 class="text-3xl font-bold mb-6">Applied Jobs</h1>
    Here you can see all of the jobs you have applied to 
    <br>


    {#if $isLoggedIn}   
<br>
        <form class="flex w-full max-w-sm items-center space-x-2 mb-4" on:submit|preventDefault={() => currentPage = 1}>
            <Input type="text" placeholder="Search applied jobs..." bind:value={searchTerm} />
            <Button type="submit">Search</Button>
        </form>

        {#if isLoading}
            <p>Loading applied jobs...</p>
        {:else if paginatedJobs.length > 0}
            <Table.Root>
                <Table.Caption>Applied Jobs</Table.Caption>
                <Table.Header>
                    <Table.Row>
                        <Table.Head class="w-[100px]">ID</Table.Head>
                        <Table.Head>Title</Table.Head>
                        <Table.Head>Company</Table.Head>
                        <Table.Head>Location</Table.Head>
                        <Table.Head>Application Date</Table.Head>
                        <Table.Head>Status</Table.Head>
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
                            <Table.Cell>{new Date(job.application_date).toLocaleDateString()}</Table.Cell>
                            <Table.Cell>{job.status}</Table.Cell>
                            <Table.Cell>
                                <Button on:click={() => openSheet(job)}>See More</Button>
                                <br>
                                <br>
                                <Button variant="destructive" on:click={() => deleteApplication(job.application_id)}>Delete Application</Button>
                                <br>
                            </Table.Cell>
                        </Table.Row>
                    {/each}
                </Table.Body>
            </Table.Root>
        {:else}
            <p>No applied jobs found.</p>
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
                            <p><strong>Company:</strong> {selectedJob?.agency}</p>
                            <br>
                            <p><strong>Location:</strong> {selectedJob?.work_location}</p>
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
                            <p><strong>Application Date:</strong> {selectedJob?.application_date}</p>
                            <br>
                            <p><strong>Application Status:</strong> {selectedJob?.status}</p>
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
    {:else}
        <p>Please log in to view your applied jobs.</p>
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
</style>