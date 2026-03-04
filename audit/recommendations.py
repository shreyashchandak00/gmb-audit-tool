from scraper.data_models import IssueType

RECOMMENDATIONS = {
    IssueType.MISSING_WEBSITE: (
        "Add your business website to your Google Maps profile. "
        "A website link builds credibility and drives traffic. "
        "If you don't have a website, consider creating a simple one using "
        "Google Sites, Wix, or WordPress. Even a single-page site with your "
        "contact info, services, and hours is better than no website."
    ),

    IssueType.LOW_RATING: (
        "Your rating is below 4.0 stars, which can deter potential customers. "
        "Focus on improving customer experience and addressing common complaints. "
        "Respond professionally to negative reviews and show you're working on improvements. "
        "Encourage satisfied customers to leave positive reviews to balance your score."
    ),

    IssueType.MODERATE_RATING: (
        "Your rating is good but could be better. Aim for 4.5+ stars to stand out. "
        "Identify patterns in lower-rated reviews and address those issues. "
        "Provide exceptional service that naturally inspires 5-star reviews. "
        "Follow up with customers after their visit to ensure satisfaction."
    ),

    IssueType.NO_REVIEWS: (
        "Your profile has no reviews, which is a major red flag for potential customers. "
        "Start by asking your most loyal customers to leave a review. "
        "Share your Google Maps review link via email, SMS, or receipts. "
        "Consider placing a QR code at your location that links directly to your review page."
    ),

    IssueType.FEW_REVIEWS: (
        "More reviews build trust and improve your local search ranking. "
        "Create a simple review request process: send a follow-up email or text "
        "after each transaction with your Google review link. "
        "Train staff to politely ask satisfied customers for reviews. "
        "Aim for at least 50 reviews to appear credible in search results."
    ),

    IssueType.NO_PHOTOS: (
        "Your profile has no photos, which dramatically reduces engagement. "
        "Profiles with photos receive 42% more direction requests and 35% more website clicks. "
        "Upload at least 10 high-quality photos showing your storefront, interior, "
        "products/services, and team. Use good lighting and a clean background."
    ),

    IssueType.FEW_PHOTOS: (
        "Add more photos to make your profile more engaging. "
        "Include a mix of: exterior shots, interior ambiance, product close-ups, "
        "team photos, and action shots of your services. "
        "Update photos seasonally to keep your profile fresh. "
        "Aim for 20+ photos for the best results."
    ),

    IssueType.NO_HOURS: (
        "Business hours are not listed on your profile. "
        "This is critical information that customers look for before visiting. "
        "Add your regular hours for all 7 days of the week. "
        "Include special hours for holidays and seasonal changes."
    ),

    IssueType.INCOMPLETE_HOURS: (
        "Your business hours are incomplete. Make sure all 7 days are listed, "
        "including days you're closed (mark them as 'Closed'). "
        "Complete hours help customers plan their visits and reduce frustration. "
        "Update them promptly for holidays or temporary changes."
    ),

    IssueType.MISSING_DESCRIPTION: (
        "Add a compelling business description to your profile. "
        "Use this space to highlight what makes your business unique, "
        "your key services, years of experience, and what customers can expect. "
        "Include relevant keywords naturally to improve search visibility. "
        "Keep it concise but informative (250-750 characters)."
    ),

    IssueType.NO_OWNER_RESPONSES: (
        "You're not responding to any customer reviews. "
        "Responding to reviews shows you value customer feedback and are actively engaged. "
        "Thank customers for positive reviews and address concerns in negative ones professionally. "
        "Aim to respond to every review within 24-48 hours. "
        "This builds trust and can improve your search ranking."
    ),

    IssueType.LOW_OWNER_RESPONSES: (
        "You're only responding to some reviews. Aim to respond to all of them. "
        "For positive reviews: thank the customer by name and mention specifics. "
        "For negative reviews: apologize, address the issue, and offer to make it right. "
        "Consistent responses show potential customers that you care about their experience."
    ),

    IssueType.MISSING_PHONE: (
        "Add a phone number to your Google Maps profile. "
        "Many customers prefer calling before visiting, especially for appointments or questions. "
        "Use a local phone number for better local SEO. "
        "If you prefer not to share a personal number, consider a Google Voice or business line."
    ),

    IssueType.MISSING_CATEGORY: (
        "Ensure your business category is properly set. "
        "The primary category is the most important factor for appearing in relevant searches. "
        "Choose the most specific category that fits your business. "
        "You can also add secondary categories to appear in more search types."
    ),
}
