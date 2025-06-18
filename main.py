from Scripts.feed import feed
from Scripts.jobatus import jobatus
from Scripts.rss import rss
from Scripts.jobsora import jobsora
from Scripts.jooble import jooble
from Scripts.jobrapido import jobrapido
from Scripts.jora import jora
from Scripts.careerjet import careerjet
from Scripts.talentcom import talentcom
from Utils.job_fetcher import fetch_all_jobs
import time


def main():
    start_time = time.time()
    job_data_list = fetch_all_jobs()
    print("Starting RSS feed generation...")
    feed(job_data_list)
    jobatus(job_data_list)
    rss(job_data_list)
    jobsora(job_data_list)
    jooble(job_data_list)
    jobrapido(job_data_list)
    jora(job_data_list)
    careerjet(job_data_list)
    talentcom(job_data_list)
    print("RSS feed generation complete.")
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
    