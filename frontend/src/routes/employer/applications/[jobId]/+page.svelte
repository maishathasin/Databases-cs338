<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { isLoggedIn, userName, logout, checkAuth } from '../../../stores/auth';
    import * as Table from "$lib/components/ui/table";
    import * as Sheet from "$lib/components/ui/sheet";
    import { Button } from "$lib/components/ui/button/index.js";
    import * as Select from "$lib/components/ui/select";
    import * as Form from "$lib/components/ui/form";
    import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import { Alert, AlertDescription, AlertTitle } from "$lib/components/ui/alert";
  import { Label } from "$lib/components/ui/label";



    const API_URL = 'http://localhost:5000';

    let selectedStatus: { value: string, label: string } | undefined;

    $: selectedStatus = newStatus
        ? { value: newStatus, label: newStatus }
        : undefined;

    interface Application {
        application_id: number;
        applicant_name: string;
        applicant_email: string;
        resume_link: string;
        cover_letter: string;
        is_student: boolean;
        university: string;
        availability: boolean;
        employment_type: string;
        phone: string;
        application_date: string;
        status: string;
    }

    let sheetOpen = false;



function closeApplicationDetails() {
  sheetOpen = false;
  selectedApplication = null;
}

    

    let jobId: number;
    let applications: Application[] = [];
    let applicationCount: number = 0;
    let selectedApplication: Application | null = null;
    let newStatus: string = '';
    let error: string | null = null;

    $: jobId = parseInt($page.params.jobId);

    onMount(async () => {
        if (!checkAuth()) {
            goto('/auth');
        } else if (isNaN(jobId)) {
            console.error('Invalid job ID');
            goto('/employer');
        } else {
            await fetchApplications();
        }
    });
    function handleStatusChange(event: CustomEvent<string>) {
        newStatus = event.detail;
    }
    async function fetchApplications() {
        error = null;
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/employer/job_applications/${jobId}`, {
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
            });

            if (response.ok) {
                const data = await response.json();
                console.log('API Response:', data);  // Log the API response

                if (Array.isArray(data)) {
                    applications = data;
                    applicationCount = data.length;
                } else if (data && typeof data === 'object' && Array.isArray(data.applications)) {
                    applications = data.applications;
                    applicationCount = data.count || data.applications.length;
                } else {
                    throw new Error('Unexpected API response format');
                }
            } else {
                throw new Error(`Failed to fetch applications: ${response.statusText}`);
            }
        } catch (err) {
            console.error('Error fetching applications:', err);
            error = err instanceof Error ? err.message : 'An unknown error occurred';
            applications = [];
            applicationCount = 0;
        }
    }
  

 
    async function updateApplicationStatus() {
        if (!selectedApplication || !newStatus) return;

        error = null;
        try {
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            if (!userData.user_id) {
                throw new Error('User ID not found in local storage');
            }

            const response = await fetch(`${API_URL}/employer/update_application_status/${selectedApplication.application_id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'User-Id': userData.user_id
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (response.ok) {
                await fetchApplications();
                selectedApplication = null;
            } else {
                throw new Error('Failed to update application status');
            }
        } catch (err) {
            console.error('Error updating application status:', err);
            error = err instanceof Error ? err.message : 'An unknown error occurred';
        }
    }

    function openApplicationDetails(application) {
    selectedApplication = application;
    sheetOpen = true;
  }

    function handleLogout() {
        logout();
        goto('/auth');
    }

    function goBack() {
        goto('/employer');
    }
</script>
<nav class="border-b-2 border-black">
    <div class="container mx-auto flex items-stretch h-16">
      <div class="flex items-center pr-4 border-r-2 border-black h-full">
        <div class="text-black font-bold  hero-text">Job Portal</div>
      </div>
      {#if $isLoggedIn}
        <div class="flex items-center space-x-4 pl-20 ml-auto ">
          
          <a href="/employer" class="text-black hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium">Dashboard</a>
          <span class="text-black text-sm">Welcome, {$userName}!</span>
          <Button variant="outline" size="sm" on:click={handleLogout}>Logout</Button>
        </div>
      {:else}
        <Button on:click={() => goto('/auth')}>Login</Button>
      {/if}
    </div>
  </nav>

<main class="container mx-auto py-8">
  <h1 class="text-3xl font-bold mb-6">Applications for Job Posting</h1>

  {#if $isLoggedIn}
    <Alert class="mb-6">
      <AlertTitle>Welcome, {$userName}!</AlertTitle>
      <AlertDescription>
        You have {applicationCount} total application{applicationCount !== 1 ? 's' : ''}.
      </AlertDescription>
    </Alert>

    <Card class="mb-6">
      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.Head>Applicant Name</Table.Head>
            <Table.Head>Email</Table.Head>
            <Table.Head>Resume</Table.Head>
            <Table.Head>Application Date</Table.Head>
            <Table.Head>Status</Table.Head>
            <Table.Head>Actions</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each applications as application}
            <Table.Row>
              <Table.Cell>{application.applicant_name}</Table.Cell>
              <Table.Cell>{application.applicant_email}</Table.Cell>
              <Table.Cell>
                {#if application.resume_link}
                  <a href={application.resume_link} target="_blank" class="text-blue-600 hover:underline">View Resume</a>
                {:else}
                  <span class="text-gray-500">No resume</span>
                {/if}
              </Table.Cell>
              <Table.Cell>{new Date(application.application_date).toLocaleDateString()}</Table.Cell>
              <Table.Cell>
                <Badge variant={application.status === 'Hired' ? 'success' : application.status === 'Rejected' ? 'destructive' : 'secondary'}>
                  {application.status}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <Button size="sm" variant="outline" on:click={() => openApplicationDetails(application)}>View Details</Button>
              </Table.Cell>
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    </Card>

    <Sheet.Root bind:open={sheetOpen}>
      <Sheet.Content>
        <Sheet.Header>
          <Sheet.Title>Application Details</Sheet.Title>
        </Sheet.Header>
        {#if selectedApplication}
          <div class="mt-4 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="font-semibold">Applicant Name</p>
                <p>{selectedApplication.applicant_name}</p>
              </div>
              <div>
                <p class="font-semibold">Email</p>
                <p>{selectedApplication.applicant_email}</p>
              </div>
              <div>
                <p class="font-semibold">Resume</p>
                {#if selectedApplication.resume_link}
                  <a href={selectedApplication.resume_link} target="_blank" class="text-blue-600 hover:underline">View Resume</a>
                {:else}
                  <span class="text-gray-500">Not provided</span>
                {/if}
              </div>
              <div>
                <p class="font-semibold">Application Date</p>
                <p>{new Date(selectedApplication.application_date).toLocaleDateString()}</p>
              </div>
              <div>
                <p class="font-semibold">Is Student</p>
                <p>{selectedApplication.is_student ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <p class="font-semibold">University</p>
                <p>{selectedApplication.university || 'Not provided'}</p>
              </div>
              <div>
                <p class="font-semibold">Availability</p>
                <p>{selectedApplication.availability ? 'Available' : 'Not available'}</p>
              </div>
              <div>
                <p class="font-semibold">Employment Type</p>
                <p>{selectedApplication.employment_type}</p>
              </div>
              <div>
                <p class="font-semibold">Phone</p>
                <p>{selectedApplication.phone}</p>
              </div>
              <div>
                <p class="font-semibold">Current Status</p>
                <Badge variant={selectedApplication.status === 'Hired' ? 'success' : selectedApplication.status === 'Rejected' ? 'destructive' : 'secondary'}>
                  {selectedApplication.status}
                </Badge>
              </div>
            </div>

            <div>
              <p class="font-semibold">Cover Letter</p>
              <p class="mt-1">{selectedApplication.cover_letter || 'Not provided'}</p>
            </div>

            <div class="mt-6">
              <Label for="new_status" class="mb-2 block">Update Status</Label>
              <div class="flex space-x-2">
                <select id="new_status" class="border rounded px-2 py-1 flex-grow" bind:value={newStatus}>
                  <option value="Applied">Applied</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Interview Scheduled">Interview Scheduled</option>
                  <option value="Offer Extended">Offer Extended</option>
                  <option value="Hired">Hired</option>
                  <option value="Rejected">Rejected</option>
                </select>
              </div>
            </div>
          </div>
          <br>
          <Sheet.Footer>
            <Button on:click={updateApplicationStatus}>Update Status</Button>
            <Button variant="outline" on:click={closeApplicationDetails}>Close</Button>
          </Sheet.Footer>
        {/if}
      </Sheet.Content>
    </Sheet.Root>
  {:else}
    <Card>
      <CardHeader>
        <CardTitle>Access Denied</CardTitle>
        <CardDescription>Please log in to view applications.</CardDescription>
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

    h1 {
        margin-bottom: 1rem;
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }
</style>