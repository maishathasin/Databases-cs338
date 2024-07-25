import { writable } from 'svelte/store';


interface UserData {
    name: string;
    email?: string;
    user_type?: string;
    redirect?: string;

    // Add any other properties that your user data might have
}


export const isLoggedIn = writable(false);
export const userName = writable('');
export const userEmail = writable('');
export const userId = writable(null);
export const userType = writable('');


export function login(userData: { name: string, [key: string]: any }) {
    console.log('Login function called with:', userData);
    isLoggedIn.set(true);
    userName.set(userData.name);
    console.log('userName set to:', userData.name);
    userEmail.set(userData.email);
    userId.set(userData.user_id);
    userType.set(userData.user_type);
    localStorage.setItem('userData', JSON.stringify(userData));
}

export function logout() {
    isLoggedIn.set(false);
    userName.set('');
    localStorage.removeItem('userData');
}

export function checkAuth() {
    const userData = localStorage.getItem('userData');
    if (userData) {
        const parsedUserData = JSON.parse(userData);
        login(parsedUserData);
        return true;
    }
    return false;
}