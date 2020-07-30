import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Variables
    result = dict()
    links = corpus[page]
    total_length = len(corpus)
    equal_probability = (1 - damping_factor) / total_length
    
    # Iterate over corpus 
    if links:
        links_probability = damping_factor / len(links)

        for page in corpus:
            result[page] = round(equal_probability, 4)

            # Add links probability
            for link in links:
                if page == link:
                    result[page] = round((result[page] + links_probability), 4)

    # Handle no links
    else:
        for page in corpus: 
            result[page] = 1 / total_length

    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Variables
    result = dict()
    samples = []
    first_sample = random.choice(list(corpus))
    current_sample = first_sample

    # Generate Samples
    for i in range(n):

        # Transition Model
        probabilities = transition_model(corpus, current_sample, damping_factor)

        # Choose sample based on weighted probabilities
        list_pages = list(probabilities)
        list_probabilities = list(probabilities.values())
        sample = random.choices(list_pages, list_probabilities)[0]
        samples.append(sample)

        # Update current sample
        current_sample = sample

    # Calculate each page's probability
    for page in corpus:

        # Count samples per page
        total_page_samples = 0
        for sample in samples:
            if sample == page:
                total_page_samples = total_page_samples + 1

        result[page] = total_page_samples / n

    return result


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Variables
    total_length = len(corpus)
    initial_rank = 1 / total_length
    first_condition = (1 - damping_factor) / total_length
    threshold = 0.001

    # Initial rank assigment
    currenk_rank = dict()
    for page in corpus:
        currenk_rank[page] = initial_rank

    # Identify pages with not links
    no_link_pages = []
    for key, value in corpus.items():
        if not value:
            no_link_pages.append(key)

    # Page Rank function
    def page_rank(current_page):
        
        # Sum of PR(i) / NumLinls(i)
        sum_links = 0

        # Handle no link pages
        if no_link_pages:
            for page in no_link_pages:
                probability = currenk_rank[page] / total_length
                sum_links = sum_links + probability

        # Handle links 
        links_to_page = []
        for key, value in corpus.items():
            if current_page in value:
                links_to_page.append(key)

        for link in links_to_page:
            link_rank = currenk_rank[link]
            number_links = len(corpus[link])
            probability = link_rank / number_links
            sum_links = sum_links + probability


        second_condition = damping_factor * sum_links

        return first_condition + second_condition

    # Iterate until every value mets threshold
    new_rank = dict()

    while True:

        # Calculate new values
        for page in currenk_rank:
            new_rank[page] = page_rank(page)

        # Validate threshold
        values_met_thresholf = 0
        for page in (corpus):
            if abs(currenk_rank[page] - new_rank[page]) < threshold:
                values_met_thresholf = values_met_thresholf + 1

        # Stop when threshold is met
        if values_met_thresholf == total_length:
            break

        # Update current rank
        for key, value in new_rank.items():
            currenk_rank[key] = value

    return new_rank


if __name__ == "__main__":
    main()
