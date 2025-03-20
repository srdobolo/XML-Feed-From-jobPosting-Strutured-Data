from Scripts.feed import feed
from Scripts.jobatus import jobatus
from Scripts.rss import rss
from Scripts.jobsora import jobsora

def main():
    print("Starting RSS feed generation...")
    feed()
    jobatus()
    rss()
    jobsora()
    print("RSS feed generation complete.")

if __name__ == "__main__":
    main()