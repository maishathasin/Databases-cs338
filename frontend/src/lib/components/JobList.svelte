<script lang="ts">
  
    import type { Job } from '../../lib/types';
  import * as Table from "$lib/components/ui/table";


  export let data
  </script>
  
  <Table.Root>
    <Table.Caption>Job Postings</Table.Caption>
    <Table.Header>
      <Table.Row>
        <Table.Head class="w-[100px]">ID</Table.Head>
        <Table.Head>Title</Table.Head>
        <Table.Head>Description</Table.Head>
        <Table.Head>Company</Table.Head>
        <Table.Head>Location</Table.Head>
      </Table.Row>
    </Table.Header>
    <Table.Body>
      {#each data.jobs as job}
        <Table.Row>
          <Table.Cell class="font-medium">{job.id}</Table.Cell>
          <Table.Cell>{job.title}</Table.Cell>
          <Table.Cell>{job.description}</Table.Cell>
          <Table.Cell>{job.company}</Table.Cell>
          <Table.Cell>{job.location}</Table.Cell>
        </Table.Row>
      {/each}
    </Table.Body>
  </Table.Root>