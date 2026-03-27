import random
from datetime import datetime, timedelta
from typing import List, Tuple
from models import Email, EmailCategory, EmailPriority


# Email templates for each category
EMAIL_TEMPLATES = {
    EmailCategory.BUG_REPORT: [
        {
            "subject": "Application crashes on startup",
            "body": "Hi, I'm experiencing a critical issue. Every time I try to launch the application, it crashes immediately with error code 0x8000. I'm on Windows 11, version 22H2. Please help urgently!",
            "priority": EmailPriority.URGENT,
            "sender": "john.smith@company.com"
        },
        {
            "subject": "Login button not working",
            "body": "Hello support team, I noticed that the login button on the mobile app doesn't respond when I tap it. I've tried restarting the app multiple times. Using iPhone 14 with latest iOS.",
            "priority": EmailPriority.HIGH,
            "sender": "sarah.jones@email.com"
        },
        {
            "subject": "Data export feature broken",
            "body": "When I try to export my data to CSV, I get an empty file. The export starts but the resulting file has 0 bytes. This worked fine last week.",
            "priority": EmailPriority.MEDIUM,
            "sender": "mike.wilson@corp.com"
        },
        {
            "subject": "Minor UI glitch in settings",
            "body": "Just noticed a small visual bug - the settings icon overlaps with the text label on smaller screens. Not urgent, but thought you should know.",
            "priority": EmailPriority.LOW,
            "sender": "emma.brown@service.com"
        },
        {
            "subject": "Cannot upload files over 10MB",
            "body": "I keep getting an error when trying to upload files larger than 10MB. The error message says 'Upload failed - file too large' but your documentation says 50MB is the limit. Please fix this.",
            "priority": EmailPriority.HIGH,
            "sender": "david.lee@business.com"
        },
        {
            "subject": "Dashboard shows incorrect metrics",
            "body": "Our analytics dashboard is displaying wrong numbers. The total user count shows 5,432 but our database has 8,901 users. This is affecting our business decisions!",
            "priority": EmailPriority.URGENT,
            "sender": "lisa.chen@analytics.com"
        },
        {
            "subject": "Search function returns no results",
            "body": "The search bar isn't working at all. No matter what I type, it says 'No results found' even for items I can see on the page.",
            "priority": EmailPriority.HIGH,
            "sender": "robert.garcia@mail.com"
        },
        {
            "subject": "Password reset email not arriving",
            "body": "I requested a password reset 3 times but haven't received any emails. I've checked spam folder too. My email is correct in my profile.",
            "priority": EmailPriority.MEDIUM,
            "sender": "anna.martinez@domain.com"
        },
    ],

    EmailCategory.FEATURE_REQUEST: [
        {
            "subject": "Please add dark mode",
            "body": "Would love to see a dark mode option in the app! I use it a lot at night and the bright white background strains my eyes. This would be a great quality of life improvement.",
            "priority": EmailPriority.MEDIUM,
            "sender": "user1@example.com"
        },
        {
            "subject": "Bulk edit functionality needed",
            "body": "It would be incredibly helpful to have the ability to edit multiple items at once. Currently I have to edit each one individually which takes hours.",
            "priority": EmailPriority.MEDIUM,
            "sender": "poweruser@company.com"
        },
        {
            "subject": "Integration with Slack",
            "body": "Our team would benefit greatly from Slack integration. We'd like to receive notifications directly in our Slack channels. Is this on your roadmap?",
            "priority": EmailPriority.LOW,
            "sender": "team.lead@startup.com"
        },
        {
            "subject": "Export to PDF feature",
            "body": "Can you add the ability to export reports as PDF? We currently have to print to PDF manually which doesn't look professional.",
            "priority": EmailPriority.LOW,
            "sender": "manager@enterprise.com"
        },
        {
            "subject": "Custom fields for user profiles",
            "body": "We need the ability to add custom fields to user profiles. Every business has different data requirements and the current fixed fields don't work for us.",
            "priority": EmailPriority.MEDIUM,
            "sender": "admin@business.com"
        },
        {
            "subject": "Mobile app for Android",
            "body": "Any plans for an Android version? I see you have iOS but half our team uses Android devices.",
            "priority": EmailPriority.LOW,
            "sender": "android.user@email.com"
        },
        {
            "subject": "Two-factor authentication",
            "body": "For security reasons, we really need 2FA support. This is becoming a requirement for our compliance.",
            "priority": EmailPriority.HIGH,
            "sender": "security.officer@corp.com"
        },
        {
            "subject": "API rate limit increase needed",
            "body": "We're hitting the API rate limit frequently. Could we get an increase or have an enterprise tier with higher limits? This is blocking our production deployment.",
            "priority": EmailPriority.HIGH,
            "sender": "developer@tech.com"
        },
    ],

    EmailCategory.BILLING: [
        {
            "subject": "Charged twice this month",
            "body": "I was charged twice for my subscription this month - once on the 1st and again on the 15th. Please refund the duplicate charge immediately. Transaction IDs: TXN12345 and TXN12389.",
            "priority": EmailPriority.URGENT,
            "sender": "customer@email.com"
        },
        {
            "subject": "Need invoice for accounting",
            "body": "Hi, I need a detailed invoice for last month's charges for our accounting department. The credit card statement isn't sufficient.",
            "priority": EmailPriority.MEDIUM,
            "sender": "accounting@company.com"
        },
        {
            "subject": "Upgrade to Enterprise plan",
            "body": "We'd like to upgrade from Pro to Enterprise plan. What's the process and will we be charged pro-rata?",
            "priority": EmailPriority.MEDIUM,
            "sender": "cto@startup.com"
        },
        {
            "subject": "Payment method update",
            "body": "Need to update our payment method. The current card on file is expiring next month.",
            "priority": EmailPriority.LOW,
            "sender": "finance@business.com"
        },
        {
            "subject": "Subscription cancellation",
            "body": "Please cancel my subscription. I'm switching to a different service. Please confirm cancellation and that I won't be charged next month.",
            "priority": EmailPriority.MEDIUM,
            "sender": "leaving.user@mail.com"
        },
        {
            "subject": "Incorrect billing amount",
            "body": "I was charged $299 but my plan is supposed to be $199/month. Please review and correct this charge.",
            "priority": EmailPriority.HIGH,
            "sender": "subscriber@domain.com"
        },
        {
            "subject": "Request for payment extension",
            "body": "Due to cash flow issues this month, we need a 15-day extension on our payment. Can you accommodate this?",
            "priority": EmailPriority.MEDIUM,
            "sender": "cfo@smallbiz.com"
        },
        {
            "subject": "Discount for annual plan?",
            "body": "Do you offer any discounts if we switch from monthly to annual billing? We're currently on the $99/month plan.",
            "priority": EmailPriority.LOW,
            "sender": "budget.conscious@email.com"
        },
    ],

    EmailCategory.GENERAL_INQUIRY: [
        {
            "subject": "How do I reset my password?",
            "body": "Hi, I forgot my password and can't figure out how to reset it. Where is the reset option?",
            "priority": EmailPriority.LOW,
            "sender": "newuser@example.com"
        },
        {
            "subject": "What's included in Pro plan?",
            "body": "I'm currently on the free tier and considering upgrading. Can you explain what additional features I get with Pro?",
            "priority": EmailPriority.LOW,
            "sender": "potential.customer@mail.com"
        },
        {
            "subject": "Browser compatibility question",
            "body": "Does your app work with Firefox? I prefer not to use Chrome.",
            "priority": EmailPriority.LOW,
            "sender": "firefox.fan@email.com"
        },
        {
            "subject": "Data retention policy",
            "body": "How long do you keep user data after account deletion? I need this information for GDPR compliance.",
            "priority": EmailPriority.MEDIUM,
            "sender": "privacy.officer@eu-company.com"
        },
        {
            "subject": "Can I transfer my account to colleague?",
            "body": "I'm leaving the company. Can I transfer my account and all its data to my replacement?",
            "priority": EmailPriority.MEDIUM,
            "sender": "departing.employee@corp.com"
        },
        {
            "subject": "System requirements",
            "body": "What are the minimum system requirements to run your desktop application?",
            "priority": EmailPriority.LOW,
            "sender": "tech.specs@email.com"
        },
        {
            "subject": "Training materials available?",
            "body": "We're rolling this out to our team of 50. Do you have training materials or documentation we can use for onboarding?",
            "priority": EmailPriority.MEDIUM,
            "sender": "training.coordinator@enterprise.com"
        },
        {
            "subject": "Downtime schedule",
            "body": "When is your regular maintenance window? We need to plan our operations around it.",
            "priority": EmailPriority.LOW,
            "sender": "operations@business.com"
        },
    ],

    EmailCategory.SPAM: [
        {
            "subject": "URGENT: Your account will be suspended!!!",
            "body": "Dear user, your account has been flagged for suspicious activity. Click here immediately to verify: http://definitely-not-phishing.ru/verify",
            "priority": EmailPriority.LOW,
            "sender": "no-reply@suspicious-domain.xyz"
        },
        {
            "subject": "You've won $1,000,000!",
            "body": "Congratulations! You've been selected as our lucky winner. Send us your bank details to claim your prize now!",
            "priority": EmailPriority.LOW,
            "sender": "lottery@scam.com"
        },
        {
            "subject": "Hot singles in your area",
            "body": "Meet attractive singles near you tonight! Click here to see profiles.",
            "priority": EmailPriority.LOW,
            "sender": "dating@spam.net"
        },
        {
            "subject": "Cheap medications online",
            "body": "Get prescription medications without prescription! 90% discount. Order now!",
            "priority": EmailPriority.LOW,
            "sender": "pharmacy@illegal.com"
        },
        {
            "subject": "RE: RE: FWD: Amazing business opportunity",
            "body": "Work from home and earn $5000 per week! No experience needed! Limited spots available!",
            "priority": EmailPriority.LOW,
            "sender": "mlm.scheme@scam.biz"
        },
        {
            "subject": "Your package is waiting",
            "body": "A package addressed to you is being held. Pay $5 redelivery fee to receive it: http://fake-shipping.com",
            "priority": EmailPriority.LOW,
            "sender": "delivery@notreal.com"
        },
    ],

    EmailCategory.ESCALATION: [
        {
            "subject": "ESCALATION: Critical production outage",
            "body": "Our entire production system has been down for 2 hours. We've lost $50k in revenue. We've contacted support 3 times with no response. This needs immediate executive attention. We need your CTO on a call NOW.",
            "priority": EmailPriority.URGENT,
            "sender": "ceo@major-client.com"
        },
        {
            "subject": "Legal threat - data breach concern",
            "body": "We believe there may have been unauthorized access to our data in your system. Our legal team is prepared to take action. We need to speak with your legal department and security officer immediately.",
            "priority": EmailPriority.URGENT,
            "sender": "legal@lawfirm.com"
        },
        {
            "subject": "Unsatisfied with support response",
            "body": "I've been trying to resolve an issue for 3 weeks with your support team (ticket #45678). Each time I get generic responses that don't address my problem. I need to speak with a manager or supervisor.",
            "priority": EmailPriority.HIGH,
            "sender": "frustrated.customer@email.com"
        },
        {
            "subject": "Contract violation - seeking resolution",
            "body": "Per our enterprise agreement, we're guaranteed 99.9% uptime. Last month we experienced 4 hours of downtime which violates our SLA. We need to discuss compensation as outlined in section 7.3 of our contract.",
            "priority": EmailPriority.HIGH,
            "sender": "contracts@big-enterprise.com"
        },
        {
            "subject": "Threatening to cancel - need retention",
            "body": "We're a 5-year customer spending $50k annually but we're seriously considering switching to your competitor due to recent service issues. Before we make this decision, we need someone from leadership to reach out.",
            "priority": EmailPriority.HIGH,
            "sender": "decision.maker@valuable-client.com"
        },
    ],

    EmailCategory.FEEDBACK: [
        {
            "subject": "Love the new dashboard!",
            "body": "Just wanted to say the new dashboard redesign is fantastic! It's so much cleaner and easier to use. Great job team!",
            "priority": EmailPriority.LOW,
            "sender": "happy.user@email.com"
        },
        {
            "subject": "Suggestion for improvement",
            "body": "Overall I like the product, but the onboarding process was confusing. Consider adding a step-by-step tutorial for new users.",
            "priority": EmailPriority.LOW,
            "sender": "constructive.user@mail.com"
        },
        {
            "subject": "Mobile app needs work",
            "body": "The mobile app feels sluggish compared to the web version. It takes 5-10 seconds to load each screen. Please optimize performance.",
            "priority": EmailPriority.MEDIUM,
            "sender": "mobile.user@example.com"
        },
        {
            "subject": "Customer service experience",
            "body": "I had an issue last week and your support agent Sarah was incredibly helpful and patient. Please pass along my thanks!",
            "priority": EmailPriority.LOW,
            "sender": "grateful.customer@email.com"
        },
        {
            "subject": "Feature request vs bug?",
            "body": "I think the way keyboard shortcuts work is inconsistent. Ctrl+S saves in some screens but not others. Is this intentional or a bug?",
            "priority": EmailPriority.LOW,
            "sender": "keyboard.warrior@tech.com"
        },
        {
            "subject": "Documentation feedback",
            "body": "Your API documentation is excellent - clear examples and well organized. However, the user guide for end users is quite outdated with old screenshots.",
            "priority": EmailPriority.LOW,
            "sender": "documentation.reader@dev.com"
        },
    ],
}

# Ambiguous emails for medium/hard tasks
AMBIGUOUS_EMAILS = [
    {
        "subject": "URGENT: Need help with the system",
        "body": "Hi, I really need help. The system isn't working right and it's affecting my work. Please help ASAP!",
        "category": EmailCategory.GENERAL_INQUIRY,  # Could be bug or inquiry
        "priority": EmailPriority.MEDIUM,  # Says urgent but vague
        "sender": "vague.user@email.com"
    },
    {
        "subject": "Billing question about features",
        "body": "I'm being charged for the Pro plan but I don't see the features listed on your pricing page. Is this a bug or am I misunderstanding what's included?",
        "category": EmailCategory.BILLING,  # Billing or feature request?
        "priority": EmailPriority.MEDIUM,
        "sender": "confused.customer@mail.com"
    },
    {
        "subject": "This is unacceptable",
        "body": "I've been a customer for 2 years and the recent changes have made this product almost unusable. The interface is confusing, features I relied on are gone, and support hasn't been helpful. I'm very disappointed.",
        "category": EmailCategory.FEEDBACK,  # Feedback or escalation?
        "priority": EmailPriority.HIGH,
        "sender": "angry.longtime.user@company.com"
    },
    {
        "subject": "Won a prize - claim now!",
        "body": "Dear valued customer, as a loyal user you've been selected for our customer appreciation program! You've won a $100 account credit. Reply to this email to claim.",
        "category": EmailCategory.SPAM,  # Looks like spam but could be real marketing
        "priority": EmailPriority.LOW,
        "sender": "marketing@our-actual-domain.com"
    },
]

# Thread emails for hard task (multi-turn conversations)
EMAIL_THREADS = [
    {
        "thread_id": "thread_001",
        "emails": [
            {
                "subject": "Cannot access my account",
                "body": "I can't log into my account. I enter my email and password but it says 'Invalid credentials'. I know my password is correct!",
                "sender": "locked.user@email.com",
                "timestamp": "2024-01-15 09:00:00",
                "reply_to": None
            },
            {
                "subject": "RE: Cannot access my account",
                "body": "Thank you for contacting us. Have you tried using the password reset link? Please try that and let us know if you still have issues.",
                "sender": "support@ourcompany.com",
                "timestamp": "2024-01-15 09:30:00",
                "reply_to": "locked.user@email.com"
            },
            {
                "subject": "RE: Cannot access my account",
                "body": "Yes I tried that already! The reset email never arrives. I've checked spam, waited hours, tried 5 times. Still nothing. This is very frustrating!",
                "sender": "locked.user@email.com",
                "timestamp": "2024-01-15 14:00:00",
                "reply_to": "support@ourcompany.com"
            }
        ],
        "category": EmailCategory.BUG_REPORT,
        "priority": EmailPriority.HIGH,
        "requires_escalation": False
    },
    {
        "thread_id": "thread_002",
        "emails": [
            {
                "subject": "Charged after cancellation",
                "body": "I cancelled my subscription on December 28th but was still charged on January 1st. Please refund immediately.",
                "sender": "ex.customer@mail.com",
                "timestamp": "2024-01-02 08:00:00",
                "reply_to": None
            },
            {
                "subject": "RE: Charged after cancellation",
                "body": "We've reviewed your account. Our records show the cancellation was processed on Dec 28, but our billing cycle closes on Dec 27. The Jan 1 charge was already scheduled. Per our terms, we can't refund this charge.",
                "sender": "billing@ourcompany.com",
                "timestamp": "2024-01-02 10:00:00",
                "reply_to": "ex.customer@mail.com"
            },
            {
                "subject": "RE: Charged after cancellation",
                "body": "This is ridiculous! I cancelled before the new year specifically to avoid this charge. Your website says cancellations are effective immediately. I want to speak with a supervisor and I'm filing a chargeback if this isn't resolved today.",
                "sender": "ex.customer@mail.com",
                "timestamp": "2024-01-02 11:30:00",
                "reply_to": "billing@ourcompany.com"
            }
        ],
        "category": EmailCategory.BILLING,
        "priority": EmailPriority.URGENT,
        "requires_escalation": True
    },
]


def generate_email(category: EmailCategory, difficulty: str = "easy", email_id: int = 0) -> Tuple[Email, EmailCategory, EmailPriority]:
    """Generate a single synthetic email with ground truth labels."""

    templates = EMAIL_TEMPLATES.get(category, [])
    if not templates:
        raise ValueError(f"No templates for category: {category}")

    template = random.choice(templates)

    # Generate timestamp
    days_ago = random.randint(0, 30)
    timestamp = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

    # Create email
    email = Email(
        id=f"email_{email_id:04d}",
        sender=template["sender"],
        subject=template["subject"],
        body=template["body"],
        timestamp=timestamp,
        has_attachment=random.random() < 0.2,  # 20% have attachments
        thread_id=None,
        reply_to=None
    )

    return email, category, template["priority"]


def generate_ambiguous_email(email_id: int = 0) -> Tuple[Email, EmailCategory, EmailPriority]:
    """Generate an ambiguous email for medium/hard difficulty."""

    template = random.choice(AMBIGUOUS_EMAILS)

    days_ago = random.randint(0, 15)
    timestamp = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

    email = Email(
        id=f"email_{email_id:04d}",
        sender=template["sender"],
        subject=template["subject"],
        body=template["body"],
        timestamp=timestamp,
        has_attachment=random.random() < 0.15,
        thread_id=None,
        reply_to=None
    )

    return email, template["category"], template["priority"]


def generate_thread_email(email_id: int = 0) -> Tuple[Email, EmailCategory, EmailPriority, bool, str]:
    """Generate an email from a multi-turn thread with context."""

    thread = random.choice(EMAIL_THREADS)
    # Return the last email in the thread (what agent sees)
    last_email = thread["emails"][-1]

    # Build context from previous emails in thread
    context = "Previous messages in this thread:\n\n"
    for i, prev_email in enumerate(thread["emails"][:-1], 1):
        context += f"[Message {i}] From: {prev_email['sender']}\n"
        context += f"Subject: {prev_email['subject']}\n"
        context += f"{prev_email['body']}\n\n"

    email = Email(
        id=f"email_{email_id:04d}",
        sender=last_email["sender"],
        subject=last_email["subject"],
        body=last_email["body"],
        timestamp=last_email["timestamp"],
        has_attachment=False,
        thread_id=thread["thread_id"],
        reply_to=last_email.get("reply_to")
    )

    return email, thread["category"], thread["priority"], thread["requires_escalation"], context


def generate_task_emails(task_id: str, count: int) -> List[Tuple[Email, EmailCategory, EmailPriority, dict]]:
    """
    Generate a full set of emails for a specific task.

    Returns list of tuples: (email, ground_truth_category, ground_truth_priority, metadata)
    """
    emails = []

    if task_id == "easy":
        # Easy: Clear-cut emails, evenly distributed across categories
        categories = list(EmailCategory)
        categories.remove(EmailCategory.ESCALATION)  # No escalations in easy

        for i in range(count):
            category = categories[i % len(categories)]
            email, gt_category, gt_priority = generate_email(category, "easy", i)
            metadata = {
                "difficulty": "easy",
                "requires_escalation": False,
                "context": None
            }
            emails.append((email, gt_category, gt_priority, metadata))

    elif task_id == "medium":
        # Medium: Mix of clear and ambiguous emails
        for i in range(count):
            if i % 3 == 0:  # 1/3 ambiguous
                email, gt_category, gt_priority = generate_ambiguous_email(i)
            else:
                category = random.choice(list(EmailCategory))
                email, gt_category, gt_priority = generate_email(category, "medium", i)

            metadata = {
                "difficulty": "medium",
                "requires_escalation": False,
                "context": None
            }
            emails.append((email, gt_category, gt_priority, metadata))

    elif task_id == "hard":
        # Hard: Mix of all types including threads
        for i in range(count):
            if i % 4 == 0:  # 1/4 are threads
                email, gt_category, gt_priority, requires_escalation, context = generate_thread_email(i)
                metadata = {
                    "difficulty": "hard",
                    "requires_escalation": requires_escalation,
                    "context": context
                }
            elif i % 4 == 1:  # 1/4 ambiguous
                email, gt_category, gt_priority = generate_ambiguous_email(i)
                metadata = {
                    "difficulty": "hard",
                    "requires_escalation": False,
                    "context": None
                }
            else:
                category = random.choice(list(EmailCategory))
                email, gt_category, gt_priority = generate_email(category, "hard", i)
                metadata = {
                    "difficulty": "hard",
                    "requires_escalation": category == EmailCategory.ESCALATION,
                    "context": None
                }

            emails.append((email, gt_category, gt_priority, metadata))

    else:
        raise ValueError(f"Unknown task_id: {task_id}")

    return emails
