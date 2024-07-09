<script lang="ts">
    import type { PageData } from './$types';
    import * as Table from "$lib/components/ui/table";
    import { Button } from "$lib/components/ui/button/index.js";
    import { goto } from '$app/navigation';
  
    interface Job {
      job_id: number;
      business_title: string;
      agency: string;
      work_location: string;
      // Add other job properties as needed
    }
  
    interface SavedJobsData extends PageData {
      savedJobs: Job[];
    }
  
    export let data: SavedJobsData;
  
    $: savedJobs = data.savedJobs;
  
    function goBack() {
      goto('/jobs');
    }
  
    async function unsaveJob(jobId: number) {
      try {
        const response = await fetch(`http://localhost:5000/unsave_job/${jobId}`, {
          method: 'DELETE',
          credentials: 'include',
        });
        if (response.ok) {
          savedJobs = savedJobs.filter(job => job.job_id !== jobId);
        } else {
          console.error('Failed to unsave job');
        }
      } catch (error) {
        console.error('Error unsaving job:', error);
      }
    }
  </script>
  
  <main>
    <h1>Saved Job Postings</h1>
  
    <Button on:click={goBack} class="mb-4">Back to All Jobs</Button>
  
    {#if savedJobs.length > 0}
      <Table.Root>
        <Table.Caption>Saved Job Postings</Table.Caption>
        <Table.Header>
          <Table.Row>
            <Table.Head class="w-[100px]">ID</Table.Head>
            <Table.Head>Title</Table.Head>
            <Table.Head>Company</Table.Head>
            <Table.Head>Location</Table.Head>
            <Table.Head>Actions</Table.Head>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {#each savedJobs as job}
            <Table.Row>
              <Table.Cell class="font-medium">{job.job_id}</Table.Cell>
              <Table.Cell>{job.business_title}</Table.Cell>
              <Table.Cell>{job.agency}</Table.Cell>
              <Table.Cell>{job.work_location}</Table.Cell>
              <Table.Cell>
                <Button on:click={() => unsaveJob(job.job_id)}>Unsave</Button>
              </Table.Cell>
            </Table.Row>
          {/each}
        </Table.Body>
      </Table.Root>
    {:else}
      <p>No saved job postings.</p>
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