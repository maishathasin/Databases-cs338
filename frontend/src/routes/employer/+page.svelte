<script lang="ts">
    import { onMount } from 'svelte';
    import type { Job } from '../../lib/types';
    import { goto } from '$app/navigation';
    import { isLoggedIn, userName, logout, checkAuth } from '../stores/auth';
    import * as Table from "$lib/components/ui/table";
    import * as Sheet from "$lib/components/ui/sheet";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import { Textarea } from "$lib/components/ui/textarea";
    import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "$lib/components/ui/card";

  import * as Dialog from "$lib/components/ui/dialog";
  import { Alert, AlertDescription, AlertTitle } from "$lib/components/ui/alert";


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

    let jobCount: number = 0;
    let totalApplications = 0;
    let topPerformingJob = {
        business_title: '',
        application_count: 0
    };

    let isCreatingDialogOpen = false;

  function openCreateJobDialog() {
    isCreatingDialogOpen = true;
  }
  function closeCreateJobDialog() {
    isCreatingDialogOpen = false;
  }

    let jobPostings: Job[] = [];
    let selectedJob: Job | null = null;
    let isCreating = false;
    let isEditing = false;
    let newJob: Job = {
        job_id: 0, // This will be set in createJobPosting
        business_title: '',
        agency: '',
        work_location: '',
        job_description: '',
        salary_range_from: '',
        salary_range_to: '',
        preferred_skills: '',
        additional_information: ''
    };

    onMount(async () => {
        await fetchDashboardData();
    });

    function generateUniqueJobId(): number {
        // Generate a unique job ID based on timestamp and a random number
        return Date.now() + Math.floor(Math.random() * 1000);
    }

    onMount(async () => {
        if (!checkAuth()) {
            goto('/auth');
        } else {
            await fetchJobPostings();
        }
    });

    async function fetchJobPostings() {
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/employer/job_postings`, {
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
            });

            if (response.ok) {
                const data = await response.json();
                jobPostings = data.job_postings;
                jobCount = data.job_count;            } 
                else {
                console.error('Failed to fetch job postings');
            }
        } catch (error) {
            console.error('Error fetching job postings:', error);
        }
    }
    async function fetchDashboardData() {
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const [totalAppsResponse, topJobResponse] = await Promise.all([
                fetch(`${API_URL}/employer/total_applications`, {
                    headers: { 'User-Id': userData.user_id }
                }),
                fetch(`${API_URL}/employer/top_performing_job`, {
                    headers: { 'User-Id': userData.user_id }
                })
            ]);

            if (totalAppsResponse.ok) {
                const data = await totalAppsResponse.json();
                totalApplications = data.total_applications;
            }

            if (topJobResponse.ok) {
                topPerformingJob = await topJobResponse.json();
            }
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
    }
    async function deleteJobPosting(jobId: number) {
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/employer/delete_job/${jobId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
            });

            if (response.ok) {
                // Remove the deleted job from the local state
                jobPostings = jobPostings.filter(job => job.job_id !== jobId);
                jobCount--;
                // If the deleted job was the selected job, clear the selection
                if (selectedJob && selectedJob.job_id === jobId) {
                    selectedJob = null;
                    isEditing = false;
                }
            } else {
                console.error('Failed to delete job posting');
            }
        } catch (error) {
            console.error('Error deleting job posting:', error);
        }
    }

    async function createJobPosting() {
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            // Generate a unique job ID
            newJob.job_id = generateUniqueJobId();

            const response = await fetch(`${API_URL}/employer/create_job`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
                body: JSON.stringify(newJob)
            });

            if (response.ok) {
                jobPostings = [...jobPostings, newJob];
                isCreating = false;
                newJob = {
                    job_id: 0,
                    business_title: '',
                    agency: '',
                    work_location: '',
                    job_description: '',
                    salary_range_from: '',
                    salary_range_to: '',
                    preferred_skills: '',
                    additional_information: ''
                };
            } else {
                console.error('Failed to create job posting');
            }
        } catch (error) {
            console.error('Error creating job posting:', error);
        }
        closeCreateJobDialog();

    }

    async function updateJobPosting() {
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/employer/update_job/${selectedJob.job_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
                body: JSON.stringify(selectedJob)
            });

            if (response.ok) {
                await fetchJobPostings();
                isEditing = false;
                selectedJob = null;
            } else {
                console.error('Failed to update job posting');
            }
        } catch (error) {
            console.error('Error updating job posting:', error);
        }
    }

    let sheetOpen = false;

function openJobDetails(job: Job) {
  selectedJob = { ...job };
  isEditing = false;
  sheetOpen = true;  // This will open the sheet
}

function closeJobDetails() {
  sheetOpen = false;
  selectedJob = null;
}
    function startEditing() {
        isEditing = true;
    }

    function cancelEditing() {
        isEditing = false;
        selectedJob = null;
    }

    function handleLogout() {
        logout();
        goto('/auth');
    }

    function viewApplications(jobId: number) {
        goto(`/employer/applications/${jobId}`);
    }
</script>

<nav class="border-b-2 border-black">
    <div class="container mx-auto flex items-stretch h-16">
      <div class="flex items-center pr-4 border-r-2 border-black h-full">
        <div class="text-black font-bold hero-text">Job Portal</div>
      </div>
      {#if $isLoggedIn}
        <div class="flex items-center space-x-4 pl-20 ml-auto ">
          <span class="text-black text-sm">Welcome, {$userName}!</span>
          <Button variant="outline" size="sm" on:click={handleLogout}>Logout</Button>
        </div>
      {:else}
        <Button on:click={() => goto('/auth')}>Login</Button>
      {/if}
    </div>
  </nav>

<main class="container mx-auto py-8">
    <h1 class="text-3xl font-bold mb-6">Employer Dashboard</h1>
  
    {#if $isLoggedIn}
      <Alert>
        <AlertTitle>Welcome, {$userName}!</AlertTitle>
        <AlertDescription>
          Manage your job postings and view applications here.
        </AlertDescription>
      </Alert>
  
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 my-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Applications</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="text-3xl font-bold">{totalApplications}</p>
          </CardContent>
        </Card>
  
        <Card>
          <CardHeader>
            <CardTitle>Top Performing Job</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="font-semibold">{topPerformingJob.business_title}</p>
            <p>{topPerformingJob.application_count} applications</p>
          </CardContent>
        </Card>
  
        <Card>
          <CardHeader>
            <CardTitle>Total Job Postings</CardTitle>
          </CardHeader>
          <CardContent>
            <p class="text-3xl font-bold">{jobCount}</p>
          </CardContent>
        </Card>
      </div>
  
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-bold">Your Job Postings</h2>
        <Button on:click={openCreateJobDialog}>Create New Job Posting</Button>
      </div>
  
      <Card>
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.Head>Title</Table.Head>
              <Table.Head>Agency</Table.Head>
              <Table.Head>Location</Table.Head>
              <Table.Head>Actions</Table.Head>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {#each jobPostings as job}
              <Table.Row>
                <Table.Cell>{job.business_title}</Table.Cell>
                <Table.Cell>{job.agency}</Table.Cell>
                <Table.Cell>{job.work_location}</Table.Cell>
                <Table.Cell>
                  <div class="flex space-x-2">
                    <Button size="sm" variant="outline" on:click={() => openJobDetails(job)}>View Details</Button>
                    <Button size="sm" variant="outline" on:click={() => viewApplications(job.job_id)}>View Applications</Button>
                    <Button size="sm" variant="destructive" on:click={() => deleteJobPosting(job.job_id)}>Delete</Button>
                  </div>
                </Table.Cell>
              </Table.Row>
            {/each}
          </Table.Body>
        </Table.Root>
      </Card>
  
      <Dialog.Root bind:open={isCreatingDialogOpen}>
        <Dialog.Content>
          <Dialog.Header>
            <Dialog.Title>Create New Job Posting</Dialog.Title>
            <Dialog.Description>
              Fill in the details for your new job posting.
            </Dialog.Description>
          </Dialog.Header>
          <form on:submit|preventDefault={createJobPosting} class="space-y-4">
            <div class="space-y-2">
              <Label for="business_title">Job Title</Label>
              <Input id="business_title" bind:value={newJob.business_title} required />
            </div>
            <div class="space-y-2">
              <Label for="agency">Agency</Label>
              <Input id="agency" bind:value={newJob.agency} required />
            </div>
            <div class="space-y-2">
              <Label for="work_location">Work Location</Label>
              <Input id="work_location" bind:value={newJob.work_location} required />
            </div>
            <div class="space-y-2">
              <Label for="job_description">Job Description</Label>
              <Textarea id="job_description" bind:value={newJob.job_description} required />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="salary_range_from">Salary Range From</Label>
                <Input type="number" id="salary_range_from" bind:value={newJob.salary_range_from} required />
              </div>
              <div class="space-y-2">
                <Label for="salary_range_to">Salary Range To</Label>
                <Input type="number" id="salary_range_to" bind:value={newJob.salary_range_to} required />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="preferred_skills">Preferred Skills</Label>
              <Input id="preferred_skills" bind:value={newJob.preferred_skills} />
            </div>
            <div class="space-y-2">
              <Label for="additional_information">Additional Information</Label>
              <Textarea id="additional_information" bind:value={newJob.additional_information} />
            </div>
            <div class="flex justify-end space-x-2">
              <Button type="button" variant="outline" on:click={closeCreateJobDialog}>Cancel</Button>
              <Button type="submit">Create Job Posting</Button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Root>
  
      {#if selectedJob}
            <Sheet.Root bind:open={sheetOpen}>
                <Sheet.Content>
                    <Sheet.Header>
                        <Sheet.Title>{selectedJob.business_title}</Sheet.Title>
                        <Sheet.Description>
                            {#if isEditing}
                                <form on:submit|preventDefault={updateJobPosting}>
                                    <Label for="edit_business_title">Job Title</Label>
                                    <Input id="edit_business_title" bind:value={selectedJob.business_title} required />

                                    <Label for="edit_agency">Agency</Label>
                                    <Input id="edit_agency" bind:value={selectedJob.agency} required />

                                    <Label for="edit_work_location">Work Location</Label>
                                    <Input id="edit_work_location" bind:value={selectedJob.work_location} required />
                                    <Label for="edit_job_description">Job Description</Label>
                                    <Textarea id="edit_job_description" bind:value={selectedJob.job_description} required />

                                    <Label for="edit_salary_range_from">Salary Range From</Label>
                                    <Input type="number" id="edit_salary_range_from" bind:value={selectedJob.salary_range_from} required />

                                    <Label for="edit_salary_range_to">Salary Range To</Label>
                                    <Input type="number" id="edit_salary_range_to" bind:value={selectedJob.salary_range_to} required />

                                    <Label for="edit_preferred_skills">Preferred Skills</Label>
                                    <Input id="edit_preferred_skills" bind:value={selectedJob.preferred_skills} />

                                    <Label for="edit_additional_information">Additional Information</Label>
                                    <Textarea id="edit_additional_information" bind:value={selectedJob.additional_information} />

                                    <Button type="submit">Update Job Posting</Button>
                                    <Button on:click={cancelEditing}>Cancel</Button>
                                </form>
                            {:else}
                                <p><strong>Agency:</strong> {selectedJob.agency}</p>
                                <p><strong>Work Location:</strong> {selectedJob.work_location}</p>
                                <p><strong>Job Description:</strong> {selectedJob.job_description}</p>
                                <p><strong>Salary Range:</strong> {selectedJob.salary_range_from} - {selectedJob.salary_range_to}</p>
                                <p><strong>Preferred Skills:</strong> {selectedJob.preferred_skills}</p>
                                <p><strong>Additional Information:</strong> {selectedJob.additional_information}</p>
                                <Button on:click={startEditing}>Edit Job Posting</Button>
                                <Button variant="outline" on:click={closeJobDetails}>Close</Button>

                            {/if}
                        </Sheet.Description>
                    </Sheet.Header>
                </Sheet.Content>
            </Sheet.Root>
      {/if}
    {:else}
      <Card>
        <CardHeader>
          <CardTitle>Access Denied</CardTitle>
          <CardDescription>Please log in to view the employer dashboard.</CardDescription>
        </CardHeader>
        <CardFooter>
          <Button on:click={() => goto('/auth')}>Go to Login</Button>
        </CardFooter>
      </Card>
    {/if}
  </main>

<style>
    main {
        padding: 1rem;
    }

    h1, h2 {
        margin-bottom: 1rem;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
    }
</style>