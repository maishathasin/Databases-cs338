<script lang="ts">
    import { goto } from '$app/navigation';
    import { Button } from "$lib/components/ui/button";
  
    function handleGetStarted() {
      goto('/auth');
    }
  </script>
  
  <div class="min-h-screen bg-white text-black flex flex-col justify-center items-center relative overflow-hidden">
    <!-- Animated background -->
    <div class="absolute inset-0 z-0">
      <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev/svgjs" viewBox="0 0 800 800" opacity="0.07">
        <defs>
          <filter id="bbblurry-filter" x="-100%" y="-100%" width="400%" height="400%" filterUnits="objectBoundingBox" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
            <feGaussianBlur stdDeviation="40" x="0%" y="0%" width="100%" height="100%" in="SourceGraphic" edgeMode="none" result="blur"></feGaussianBlur>
          </filter>
        </defs>
        <g filter="url(#bbblurry-filter)">
          <ellipse rx="138.5" ry="139" cx="369.6738177446374" cy="574.3185107267541" fill="hsl(0, 0%, 0%)"></ellipse>
          <ellipse rx="138.5" ry="139" cx="464.08350270433015" cy="262.248251463326" fill="hsl(0, 0%, 10%)"></ellipse>
          <ellipse rx="138.5" ry="139" cx="186.4811298009638" cy="336.3443522592492" fill="hsl(0, 0%, 20%)"></ellipse>
        </g>
      </svg>
    </div>
  
    <main class="z-10 text-center px-4">
      <h1 class="text-5xl md:text-7xl font-bold mb-6 animate-fade-in">
        Top Data Science Jobs
      </h1>
      <p class="text-xl md:text-2xl mb-12 animate-fade-in-delay">
        Discover your next career opportunity in the world of data.
      </p>
      <Button 
        size="lg" 
        variant="outline"
        class="text-lg px-8 py-3 border-2 border-black hover:bg-black hover:text-white transition-colors duration-300 animate-fade-in-delay-2"
        on:click={handleGetStarted}
      >
        Get Started
      </Button>
    </main>
  </div>
  
  <style>
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
  
    .animate-fade-in {
      animation: fadeIn 0.8s ease-out forwards;
    }
  
    .animate-fade-in-delay {
      animation: fadeIn 0.8s ease-out 0.2s forwards;
      opacity: 0;
    }
  
    .animate-fade-in-delay-2 {
      animation: fadeIn 0.8s ease-out 0.4s forwards;
      opacity: 0;
    }
  
    /* Ensure the button text remains black on hover */
    :global(.dark) .text-black {
      color: black !important;
    }
  </style>