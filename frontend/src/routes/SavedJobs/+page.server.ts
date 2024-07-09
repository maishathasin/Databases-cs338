import type { PageServerLoad } from './$types';

interface Job {
  job_id: number;
  business_title: string;
  agency: string;
  work_location: string;
  // Add other job properties as needed
}

export const load: PageServerLoad = async ({ fetch }): Promise<{ savedJobs: Job[] }> => {
  try {
    const response = await fetch('http://localhost:5000/saved_jobs', {
      credentials: 'include'
    });
    
    if (response.ok) {
      const savedJobs: Job[] = await response.json();
      return { savedJobs };
    } else {
      console.error('Failed to fetch saved jobs');
      return { savedJobs: [] };
    }
  } catch (error) {
    console.error('Error fetching saved jobs:', error);
    return { savedJobs: [] };
  }
};