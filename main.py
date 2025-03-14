from feed import generate_feed1
from jobatus import generate_feed2

def main():
    print("Starting RSS feed generation...")
    generate_feed1()
    generate_feed2()
    print("RSS feed generation complete.")

if __name__ == "__main__":
    main()