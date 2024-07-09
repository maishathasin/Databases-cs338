export type Categories = 'sveltekit' | 'svelte'

export type Job = {
	job_id: number;
	agency: string;
	Posting_type: string; 
	business_title: string;
	salary_range_from: string;
	salary_range_to: string;
	work_location: string;
	additional_information:string;
	preferred_skills:string;
	job_description:string;
}

