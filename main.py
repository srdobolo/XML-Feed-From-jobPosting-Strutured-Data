from Scripts.feed import feed
from Scripts.jobatus import jobatus
from Scripts.rss import rss
from Scripts.jobsora import jobsora
from Scripts.jooble import jooble
from Scripts.jobrapido import jobrapido
from Scripts.jora import jora
from Scripts.careerjet import careerjet
from Scripts.talentcom import talentcom

def main():
    print("Starting RSS feed generation...")
    feed()
    jobatus()
    rss()
    jobsora()
    jooble()
    jobrapido()
    jora()
    careerjet()
    talentcom()
    print("RSS feed generation complete.")

if __name__ == "__main__":
    main()