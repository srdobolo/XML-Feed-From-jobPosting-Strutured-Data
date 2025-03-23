from Scripts.feed import feed
from Scripts.jobatus import jobatus
from Scripts.rss import rss
from Scripts.jobsora import jobsora
from Scripts.jooble import jooble
from Scripts.jobrapido import jobrapido
from Scripts.jora import jora

def main():
    print("Starting RSS feed generation...")
    feed()
    jobatus()
    rss()
    jobsora()
    jooble()
    jobrapido()
    jora()
    print("RSS feed generation complete.")

if __name__ == "__main__":
    main()