<script lang="ts">
    import { onMount } from 'svelte';
    import { Button } from "$lib/components/ui/button/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import { Checkbox } from "$lib/components/ui/checkbox/index.js";
    import { goto } from '$app/navigation';
    import { isLoggedIn, userName, logout, checkAuth } from '../stores/auth';
    import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "$lib/components/ui/select";
  import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "$lib/components/ui/card";
  import { Alert, AlertDescription, AlertTitle } from "$lib/components/ui/alert";
  import { Textarea } from "$lib/components/ui/textarea";

  
    let profile = {
      name: '',
      resume_link: '',
      cover_letter: '',
      is_student: false,
      university: '',
      availability: false,
      employment_type: '',
      phone: ''
    };
  
    let errorMessage = '';
    let successMessage = '';
  
    const API_URL = 'http://localhost:5000';
  
    onMount(() => {
      if (!checkAuth()) {
        goto('/auth');
      } else {
        fetchProfile();
      }
    });
  
    async function fetchProfile() {
      try {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        if (!userData.user_id) {
          throw new Error('User ID not found in local storage');
        }
        const response = await fetch(`${API_URL}/applicant_profile`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'User-Id': userData.user_id
          },
        });
        if (response.ok) {
          const data = await response.json();
          profile = data;
          userName.set(data.name);
        } else if (response.status === 404) {
          console.log('Profile not found, creating new profile');
          const data = await response.json();
          if (data.name) {
            userName.set(data.name);
          }
        } else {
          errorMessage = 'Failed to fetch profile';
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
        errorMessage = 'Error fetching profile. Please try again.';
      }
    }
  
    async function updateProfile() {
      try {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        if (!userData.user_id) {
          throw new Error('User ID not found in local storage');
        }
        const response = await fetch(`${API_URL}/applicant_profile`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-Id': userData.user_id
          },
          body: JSON.stringify(profile),
        });
        if (response.ok) {
          const data = await response.json();
          successMessage = data.message || 'Profile updated successfully';
          if (data.name) {
            userName.set(data.name);
          }
          errorMessage = '';
        } else {
          const errorData = await response.json();
          errorMessage = errorData.message || 'Failed to update profile';
          successMessage = '';
        }
      } catch (error) {
        console.error('Error updating profile:', error);
        errorMessage = 'Error updating profile. Please try again.';
        successMessage = '';
      }
    }
  
    function handleLogout() {
      logout();
      goto('/auth');
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
  
  <main class="container mx-auto py-8 max-w-2xl">
    <Card>
      <CardHeader>
        <CardTitle class="text-2xl">Applicant Profile</CardTitle>
        <CardDescription>Welcome, {$userName}! Update your profile below:</CardDescription>
      </CardHeader>
      <CardContent>
        {#if errorMessage}
          <Alert variant="destructive" class="mb-4">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        {/if}
  
        {#if successMessage}
          <Alert variant="default" class="mb-4">
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        {/if}
  
        <form on:submit|preventDefault={updateProfile} class="space-y-6">
          <div class="space-y-2">
            <Label for="resume_link">Resume Link</Label>
            <Input type="text" id="resume_link" bind:value={profile.resume_link} />
          </div>
  
          <div class="space-y-2">
            <Label for="cover_letter">Cover Letter</Label>
            <Textarea id="cover_letter" bind:value={profile.cover_letter} />
          </div>
  
          <div class="flex items-center space-x-2">
            <Checkbox id="is_student" bind:checked={profile.is_student} />
            <Label for="is_student">Are you a student?</Label>
          </div>
  
          {#if profile.is_student}
            <div class="space-y-2">
              <Label for="university">University</Label>
              <Input type="text" id="university" bind:value={profile.university} />
            </div>
          {/if}
  
          <div class="flex items-center space-x-2">
            <Checkbox id="availability" bind:checked={profile.availability} />
            <Label for="availability">Are you available for immediate start?</Label>
          </div>
  
          <div class="space-y-2">
            <Label for="employment_type">Employment Type</Label>
              <select id="employment_type" bind:value={profile.employment_type}>       
                    <option value="full_time">Full Time</option>       
                        <option value="part_time">Part Time</option>    
                               <option value="contract">Contract</option>     
                                     <option value="internship">Internship</option>    
                              </select>      
          </div>
  
          <div class="space-y-2">
            <Label for="phone">Phone Number</Label>
            <Input type="tel" id="phone" bind:value={profile.phone} />
          </div>
  
          <Button type="submit" class="w-full">Update Profile</Button>
        </form>
      </CardContent>
      <CardFooter class="flex justify-between">
        <Button variant="outline" on:click={() => goto('/jobs')}>Back to Job Listings</Button>
        <Button variant="destructive" on:click={handleLogout}>Logout</Button>
      </CardFooter>
    </Card>
  </main>
  <style>
    main {
      padding: 1rem;
      max-width: 600px;
      margin: 0 auto;
    }
  
    form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
  
    textarea {
      width: 100%;
      height: 100px;
    }
  
    .error {
      color: red;
      font-weight: bold;
    }
  
    .success {
      color: green;
      font-weight: bold;
    }
  </style>