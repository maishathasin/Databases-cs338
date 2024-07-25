// Flask App (app.py)
// Svelte Component (+page.server.ts)
import type { Job } from '$lib/types';
import type { PageServerLoad, Actions } from './$types';
import { writable } from 'svelte/store';



let jobs: Job[] = [];
let selectedJob: Job | null = null;
const isLoggedIn = writable(false);
const userName = writable('');
let searchTerm = '';
let email = '';
let password = '';

export const load: PageServerLoad = async ({ fetch, cookies }) => {
  const sessionCookie = cookies.get('session');
  const rememberCookie = cookies.get('remember_token');
  
  console.log('Session cookie:', sessionCookie);
  console.log('Remember cookie:', rememberCookie);

  try {
    const jobsResponse = await fetch('http://127.0.0.1:5000/jobs', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (jobsResponse.status === 401) {
      return {
        jobs: [],
        isLoggedIn: false,
        userName: '',
        error: 'User not authenticated'

      };
    }

    if (!jobsResponse.ok) {
      throw new Error(`HTTP error! status: ${jobsResponse.status}`);
    }

    const jobs: Job[] = await jobsResponse.json();


    async function login() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        });
        if (response.ok) {
          const userData = await response.json();
          console.log('Login successful:', userData);
          isLoggedIn = true;
          userName = userData.name;
          localStorage.setItem('userData', JSON.stringify(userData));
          await fetchJobs();
        } else {
          console.error('Login failed');
        }
      } catch (error) {
        console.error('Error during login:', error);
      }
    }
  
    function logout() {
      isLoggedIn = false;
      userName = '';
      localStorage.removeItem('userData');
      jobs = [];
    }

    const authResponse = await fetch('http://127.0.0.1:5000/check_auth', {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Cookie': `session=${sessionCookie || ''}`,
      },
    });
    const authResult = await authResponse.json();

    const isLoggedIn = authResult.authenticated;
    const userName = authResult.name || '';

    return { jobs, isLoggedIn, userName };
  } catch (error) {
    console.error('Error in load function:', error);
    return {
      jobs: [],
      isLoggedIn: false,
      userName: '',
      error: 'An error occurred while fetching data',
    };
  }
};

export const actions: Actions = {
  apply: async ({ request, fetch }) => {
    const formData = await request.formData();
    const jobId = formData.get('job_id');

    try {
      const response = await fetch('http://127.0.0.1:5000/apply', {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId }),
        credentials: 'include',
      });

      if (response.ok) {
        return { success: true };
      } else if (response.status === 401) {
        return { success: false, message: 'User not authenticated' };
      } else {
        return { success: false, message: 'Failed to apply for job' };
      }
    } catch (error) {
      console.error('Error applying for job:', error);
      return { success: false, message: 'An unexpected error occurred' };
    }
  }
};