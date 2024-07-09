import type { Job } from '$lib/types';
import type { Load, Actions } from '@sveltejs/kit';

export const load: Load = async ({ fetch }) => {
  try {
    const response = await fetch('http://127.0.0.1:5000/jobs');
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const jobs: Job[] = await response.json();
    
    return { jobs };
  } catch (error) {
    console.error('Error in +page.server.ts:', error);
    return {
      status: 500,
      error: 'Internal Server Error'
    };
  }
};
