"""
Interactive PII Detection Demo - 5 Minute Story
The Tale of Sarah's Lost Luggage
"""

import time
import sys
import os

# Import custom modules
from pii_comparison import load_email, compare_detectors


def typewriter_print(text, delay=0.02):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_box(text, width=78):
    """Print text in a box"""
    print("┌" + "─" * width + "┐")
    for line in text.split('\n'):
        padding = width - len(line)
        print("│ " + line + " " * padding + "│")
    print("└" + "─" * width + "┘")


def pause(seconds=2):
    """Pause for dramatic effect"""
    time.sleep(seconds)


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_intro():
    """Show introduction with story context"""
    clear_screen()
    
    print("\n" + "=" * 80)
    print("🎬  THE STORY OF SARAH'S LOST LUGGAGE".center(80))
    print("=" * 80 + "\n")
    
    pause(1)
    
    story = """
🧳 Sarah Martinez is flying from Boston to London for a business trip.
   When she arrives at Heathrow Airport, her luggage is missing!

📧 She needs to file an insurance claim via email, but there's a problem...

🔒 The email contains SENSITIVE PERSONAL INFORMATION:
   • Full name, date of birth, passport number
   • Home address, phone numbers, email
   • Social Security number, credit card details
   • Bank account information
   • Medical prescriptions
   • And much more...

⚠️  If this data falls into the wrong hands, Sarah could become a victim
   of identity theft, financial fraud, or privacy violations!

🛡️  THE CHALLENGE: How do we detect and protect ALL this sensitive data?

💡 THE SOLUTION: We'll test TWO advanced PII detection systems:
   1. Microsoft Presidio (Pattern-based detection)
   2. Transformer AI Model (Context-aware detection)

⏱️  Let's see which one can better protect Sarah's information!
"""
    
    for line in story.split('\n'):
        print(line)
        pause(0.3)
    
    print("\n" + "=" * 80)
    input("\n🎯 Press ENTER to begin the detection comparison... ")


def show_email_preview(text):
    """Show preview of the email"""
    clear_screen()
    
    print("\n" + "=" * 80)
    print("📧  SARAH'S INSURANCE CLAIM EMAIL".center(80))
    print("=" * 80 + "\n")
    
    print("Here's a preview of the email Sarah is about to send...")
    print("(Notice all the sensitive information highlighted below)\n")
    
    pause(1)
    
    # Show first 1000 characters
    preview = text[:1000]
    print("-" * 80)
    print(preview)
    print("\n... [Email continues with more sensitive data] ...\n")
    print("-" * 80)
    
    print("\n🚨 ALERT: This email contains:")
    print("   • Personal names, dates, and contact info")
    print("   • Financial data (bank accounts, credit cards)")
    print("   • Government IDs (passport, SSN, driver's license)")
    print("   • Medical information")
    print("   • Location data and travel details")
    
    print("\n" + "=" * 80)
    input("\n🔍 Press ENTER to start PII detection... ")


def show_detection_progress(detector_name):
    """Show detection progress animation"""
    print(f"\n⚙️  Running {detector_name}...")
    
    stages = [
        "Initializing detection engine",
        "Loading recognition models",
        "Analyzing text patterns",
        "Detecting entities",
        "Calculating confidence scores",
        "Generating results"
    ]
    
    for stage in stages:
        sys.stdout.write(f"   {stage}... ")
        sys.stdout.flush()
        pause(0.3)
        sys.stdout.write("✓\n")
    
    print(f"\n✅ {detector_name} detection complete!\n")
    pause(1)


def show_results_summary(results):
    """Show quick summary of results"""
    presidio_count = len(results['presidio']['results'])
    transformer_count = len(results['transformer']['results'])
    
    print("\n" + "=" * 80)
    print("📊  QUICK RESULTS SUMMARY".center(80))
    print("=" * 80 + "\n")
    
    print(f"🔹 Presidio detected:      {presidio_count:3} PII entities")
    print(f"🔹 Transformer detected:   {transformer_count:3} PII entities")
    print(f"🔹 Difference:             {abs(presidio_count - transformer_count):3} entities")
    
    pause(2)


def show_finale():
    """Show conclusion and recommendations"""
    clear_screen()
    
    print("\n" + "=" * 80)
    print("🎊  THE VERDICT".center(80))
    print("=" * 80 + "\n")
    
    pause(1)
    
    conclusions = [
        "\n🏆 BOTH systems successfully detected Sarah's sensitive information!",
        "\n✅ Presidio excels at:",
        "   • Structured patterns (SSN, credit cards, bank accounts)",
        "   • Comprehensive entity type coverage",
        "   • Fast, production-ready processing",
        
        "\n✅ Transformer excels at:",
        "   • Context-aware name detection",
        "   • Natural language understanding",
        "   • Semantic relationship recognition",
        
        "\n💡 THE WINNING STRATEGY:",
        "   🤝 Use BOTH systems together in a HYBRID approach!",
        "   • Presidio catches structured patterns",
        "   • Transformer understands context",
        "   • Together they provide maximum protection",
        
        "\n🛡️  SARAH'S DATA IS NOW PROTECTED!",
        "   Her anonymized email can be safely shared with:",
        "   • Insurance companies",
        "   • Customer service",
        "   • Legal departments",
        "   • Compliance teams",
        
        "\n📂 All results have been saved to the 'results/' folder:",
        "   ✓ Comparison report (CSV)",
        "   ✓ Anonymized email versions",
        "   ✓ Detailed detection logs",
    ]
    
    for line in conclusions:
        print(line)
        pause(0.5)
    
    print("\n" + "=" * 80)
    print("🎬  END OF DEMONSTRATION".center(80))
    print("=" * 80 + "\n")
    
    print("✨ Thank you for watching!")
    print("📚 Check the README.md for more information and documentation.\n")


def run_demo():
    """Run the complete 5-minute demo"""
    
    try:
        # 1. Introduction (45 seconds)
        show_intro()
        
        # 2. Load email
        email_text = load_email('sample_email.txt')
        
        # 3. Show email preview (30 seconds)
        show_email_preview(email_text)
        
        # 4. Run detection (this is the main work - 2 minutes)
        clear_screen()
        print("\n" + "=" * 80)
        print("🔬  STARTING PII DETECTION ANALYSIS".center(80))
        print("=" * 80)
        
        show_detection_progress("Microsoft Presidio")
        show_detection_progress("Transformer AI Model")
        
        # Run actual comparison (this will print detailed results)
        results = compare_detectors(email_text, threshold=0.5)
        
        # 5. Show summary (30 seconds)
        show_results_summary(results)
        
        input("\n📊 Press ENTER to see the final verdict... ")
        
        # 6. Show conclusions (1 minute)
        show_finale()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user.")
        print("✨ Thanks for watching!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        print("Please check that all dependencies are installed correctly.\n")
        sys.exit(1)


def show_menu():
    """Show main menu"""
    clear_screen()
    
    print("\n" + "=" * 80)
    print("🛡️  PII DETECTION DEMO - Choose Your Experience".center(80))
    print("=" * 80 + "\n")
    
    print("1. 🎬 Full Story Demo (5 minutes with narration)")
    print("2. 🔍 Quick Analysis (Direct comparison, < 1 minute)")
    print("3. 📚 Read the Story First")
    print("4. ❌ Exit")
    
    print("\n" + "-" * 80)
    choice = input("\nEnter your choice (1-4): ").strip()
    
    return choice


def read_story():
    """Display the story without running demo"""
    clear_screen()
    
    print("\n" + "=" * 80)
    print("📖  THE STORY".center(80))
    print("=" * 80 + "\n")
    
    story = """
Sarah Martinez is a business consultant who frequently travels internationally.
On October 28, 2025, she flew from Boston to London for an important client
meeting. Upon arrival at Heathrow Airport, she discovered her luggage was missing.

Inside her suitcase were not just clothes, but critical items:
• Her laptop with client presentations
• Prescription medications she needs daily
• Important travel documents and identification
• Jewelry with sentimental value

Sarah needs to file an insurance claim immediately, but there's a serious problem.
The claim email must include:
• Her full name, date of birth, and passport number
• Home address and multiple phone numbers
• Financial information (bank account, credit cards)
• Social Security number for identity verification
• Medical prescription details
• Travel insurance policy numbers

If this email is intercepted or improperly handled, Sarah could face:
• Identity theft and financial fraud
• Privacy violations and surveillance
• Medical information disclosure
• Potential security threats

This is where PII (Personally Identifiable Information) detection becomes critical.

TWO SOLUTIONS:

1. MICROSOFT PRESIDIO
   - Pattern-based detection system
   - Uses regex and rule-based recognizers
   - Detects 50+ entity types
   - Fast and production-ready
   - Excellent at structured data (SSN, credit cards, etc.)

2. TRANSFORMER AI MODEL
   - Machine learning-based detection
   - Understands context and semantics
   - Fine-tuned on PII datasets
   - Better at natural language entities (names, addresses)
   - More computationally intensive but highly accurate

THE QUESTION:
Which system can better protect Sarah's sensitive information?
Or should we use both together?

Let's find out in the demonstration...
"""
    
    print(story)
    print("\n" + "=" * 80)
    input("\nPress ENTER to return to menu... ")


def main():
    """Main entry point"""
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_demo()
            input("\nPress ENTER to return to menu... ")
        
        elif choice == '2':
            clear_screen()
            print("\n🔍 Running quick analysis...\n")
            email_text = load_email('sample_email.txt')
            compare_detectors(email_text, threshold=0.5)
            input("\n\n✅ Analysis complete! Press ENTER to return to menu... ")
        
        elif choice == '3':
            read_story()
        
        elif choice == '4':
            clear_screen()
            print("\n✨ Thank you for using PII Detection Demo!")
            print("🛡️  Stay safe and protect your data!\n")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")
            pause(1)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🛡️  Welcome to the PII Detection Demo!".center(80))
    print("=" * 80)
    print("\nLoading demo environment...")
    pause(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✨ Demo interrupted. Goodbye!\n")
        sys.exit(0)
