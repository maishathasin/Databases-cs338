<script lang="ts">
    import * as Tabs from "$lib/components/ui/tabs/index.js";
    import * as Card from "$lib/components/ui/card/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Input } from "$lib/components/ui/input/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import { enhance } from "$app/forms";
    import { goto } from '$app/navigation';
    import type { ActionResult } from '@sveltejs/kit';
    import { Toaster } from "$lib/components/ui/sonner";


    let name: string = '';
    let email: string = '';
    let password: string = '';
    let userType: string = 'applicant';

    let loginEmail: string = '';
    let loginPassword: string = '';

    let message: string | null = null;
    let isLoggedIn: boolean = false;


    function handleSubmit() {
        return async ({ result }: { result: ActionResult }) => {
            if (result.type === 'success') {
                if (result.data && typeof result.data === 'object' && 'redirect' in result.data) {
                    // Handle redirect
                    isLoggedIn = true;
                    goto(result.data.redirect as string);
                } else {
                    message = "Operation successful";
                }
            } else if (result.type === 'failure') {
                message = result.data?.message as string || "An error occurred";
            } else {
                message = "An unexpected error occurred";
            }
        }
    }


  


</script>
<div class="container">

    {#if !isLoggedIn}


<Tabs.Root value="register" class="w-[400px]">
    <Tabs.List class="grid w-full grid-cols-2">
        <Tabs.Trigger value="register">Register</Tabs.Trigger>
        <Tabs.Trigger value="login">Login</Tabs.Trigger>
    </Tabs.List>
    <Tabs.Content value="register">
        <Card.Root>
            <Card.Header>
                <Card.Title>Register</Card.Title>
                <Card.Description>
                    Create a new account.
                </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2">
                <form method="POST" action="?/register" use:enhance={handleSubmit}>
                    <div class="space-y-1">
                        <Label for="name">Name</Label>
                        <Input id="name" name="name" bind:value={name} />
                    </div>
                    <div class="space-y-1">
                        <Label for="email">Email</Label>
                        <Input id="email" name="email" bind:value={email} />
                    </div>
                    <div class="space-y-1">
                        <Label for="password">Password</Label>
                        <Input id="password" name="password" type="password" bind:value={password} />
                    </div>
                    <br>
                
                    <div class="space-y-1">
                        <Label for="userType">User Type</Label>
                        <select id="userType" name="user_type" bind:value={userType}>
                            <option value="applicant">Applicant</option>
                            <option value="employer">Employer</option>
                        </select>
                    </div>
                    <br>
                    <Card.Footer>
                        <Button type="submit">Register</Button>
                    </Card.Footer>
                </form>
            </Card.Content>
        </Card.Root>
    </Tabs.Content>
    <Tabs.Content value="login">
        <Card.Root>
            <Card.Header>
                <Card.Title>Login</Card.Title>
                <Card.Description>
                    Access your account.
                </Card.Description>
            </Card.Header>
            <Card.Content class="space-y-2">
                <form method="POST" action="?/login" use:enhance={handleSubmit}>
                    <div class="space-y-1">
                        <Label for="loginEmail">Email</Label>
                        <Input id="loginEmail" name="email" bind:value={loginEmail} />
                    </div>
                    <div class="space-y-1">
                        <Label for="loginPassword">Password</Label>
                        <Input id="loginPassword" name="password" type="password" bind:value={loginPassword} />
                    </div>
                    <br>
                    <Card.Footer>
                        <Button type="submit">Login</Button>
                    </Card.Footer>
                </form>
            </Card.Content>
        </Card.Root>
    </Tabs.Content>
</Tabs.Root>
{:else}
        <p>You are already logged in.</p>
        <Button on:click={() => goto('/jobs')}>Go to Dashboard</Button>
    {/if}

</div>

{#if message}
    <p>{message}</p>
{/if}

<style>
    .container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    width: 100%;
    padding: 20px;
    box-sizing: border-box;
}

@media (max-width: 480px) {
    .container {
        padding: 10px;
    }
}
</style>