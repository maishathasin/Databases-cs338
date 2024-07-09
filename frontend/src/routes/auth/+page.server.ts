import type { Actions } from '@sveltejs/kit';
import { redirect } from '@sveltejs/kit';


export const actions: Actions = {
  register: async ({ request }) => {
    const formData = await request.formData();
    const name = formData.get('name');
    const email = formData.get('email');
    const password = formData.get('password');
    const userType = formData.get('user_type');

    try {
      const response = await fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password, user_type: userType }),
      });

      if (response.ok) {
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, message: error.error };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, message: 'An unexpected error occurred' };
    }
  },

  login: async ({ request, url }) => {
    console.log('Current URL before login attempt:', url.toString());
    
    const formData = await request.formData();
    const email = formData.get('email');
    const password = formData.get('password');
    
    try {
      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      const responseText = await response.text();
      console.log('Raw response:', responseText);
      
      if (response.ok) {
        const data = JSON.parse(responseText);
        console.log('Login successful:', data);
        
        const redirectUrl = '/jobs';
        console.log('Attempting to redirect to:', new URL(redirectUrl, url).toString());
        
        // Return a custom response object instead of using redirect
        return {
          success: true,
          redirect: redirectUrl,
          message: 'Login successful'
        };
      } else {
        console.error('Login failed:', responseText);
        return { success: false, message: 'Login failed. Please check your credentials and try again.' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, message: 'An unexpected error occurred' };
    }
  }
};