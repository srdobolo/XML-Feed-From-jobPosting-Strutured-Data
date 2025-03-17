from Scripts.feed import generate_feed1
from Scripts.jobatus import generate_feed2
from Scripts.rss import generate_feed3
from Scripts.jobsora import generate_feed4

def main():
    print("Starting RSS feed generation...")
    generate_feed1()
    generate_feed2()
    generate_feed3()
    generate_feed4()
    print("RSS feed generation complete.")

if __name__ == "__main__":
    main()