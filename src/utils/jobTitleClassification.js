// Define the logic for red bubbles (IT Specialist variations) in one place
export function isRedBubble(jobTitle) {
    const title = jobTitle?.toUpperCase() || '';
    const hasSpecialist = title.includes('SPECIALIST');
    const hasIT = title.includes('IT');
    const hasInfoTech = title.includes('INFORMATION TECHNOLOGY');
    const hasProgramManager = title.includes('PROGRAM MANAGER');
    const hasITSPEC = title.includes('ITSPEC');
    
    const isITSpecialist = hasSpecialist && (hasIT || hasInfoTech);
    const isITProgramManager = hasProgramManager && (hasIT || hasInfoTech);
    
    return isITSpecialist || isITProgramManager || hasITSPEC;
}

// Get the color for a job title
export function getJobTitleColor(jobTitle) {
    return isRedBubble(jobTitle) ? '#A34131' : '#4FB477';
}