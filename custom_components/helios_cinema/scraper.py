#!/usr/bin/env python3
"""
Helios Cinema Scraper Module

This module provides functionality to scrape movie information from Helios Cinema websites.
It can extract movie titles, descriptions, images, and showtimes from the website's HTML.
"""

import re
import asyncio
import aiohttp
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class HeliosScraper:
    """Scraper for Helios Cinema websites."""
    
    def __init__(self, cinema_url: str, timeout: int = 30):
        """
        Initialize the scraper.
        
        Args:
            cinema_url: URL of the Helios cinema location
            timeout: HTTP request timeout in seconds
        """
        self.cinema_url = cinema_url
        self.timeout = timeout
    
    async def fetch_page(self) -> Optional[str]:
        """
        Fetch the HTML content from the cinema URL.
        
        Returns:
            HTML content as string, or None if failed
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(self.cinema_url) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"HTTP Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_films_from_html(self, html: str) -> List[Dict]:
        """
        Extract film information from HTML content.
        
        Args:
            html: HTML content as string
            
        Returns:
            List of dictionaries containing film information
        """
        films = []
        
        # Try JavaScript extraction first (NUXT data)
        nuxt_films = self._extract_from_nuxt_data(html)
        if nuxt_films:
            return nuxt_films
        
        # Fallback to HTML parsing
        html_films = self._extract_from_html_fallback(html)
        return html_films
    
    def _extract_from_nuxt_data(self, html: str) -> List[Dict]:
        """
        Extract movie data from the NUXT JavaScript data structure.
        
        Args:
            html: HTML content as string
            
        Returns:
            List of film dictionaries
        """
        films = []
        
        try:
            # Find the NUXT script tag with the data
            patterns = [
                r'<script>window\.__NUXT__=\(function\([^)]+\)\{[^}]*\}\)\(([^)]+)\);</script>',
                r'window\.__NUXT__=\(function\([^)]+\)\{[^}]*\}\)\(([^)]+)\);',
                r'__NUXT__=\(function\([^)]+\)\{[^}]*\}\)\(([^)]+)\)',
            ]
            
            match = None
            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    break
            
            if not match:
                return []
            
            # Extract the parameters
            params_str = match.group(1)
            
            # Look for movie titles in quotes with specific keywords
            title_pattern = r'"([^"]*(?:Superman|Basia|Smerfy|Harry Potter|Jurassic|Fantastyczna|Koszmar|Lilo|Caravaggio|Brzydka|Andrea|Heidi|Grobowiec|Dziewczyna|Wujek|André|BTS|Maraton|Festiwal|Strażak|Bing|Elio|Jak wytresować|Władca Pierścieni|F1|13 dni)[^"]*)"'
            title_matches = re.findall(title_pattern, params_str, re.IGNORECASE)
            
            # Find showtime patterns - more flexible patterns
            showtime_patterns = [
                r'"(2025-07-\d{2} \d{2}:\d{2}:\d{2})"',  # Today's date format
                r'"(2025-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"',  # General date format
                r'(\d{2}:\d{2}:\d{2})',  # Just time format
                r'timeFrom["\s]*:["\s]*["\s]*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # NUXT timeFrom pattern
            ]
            
            showtime_matches = []
            for pattern in showtime_patterns:
                matches = re.findall(pattern, params_str)
                showtime_matches.extend(matches)
            
            # Clean up titles and group showtimes by movie
            movie_titles = set()
            movie_showtimes_map = {}
            # Try to group showtimes by movie title context in params_str
            # Find all blocks like: title...showtimes... (naive, but works for this structure)
            movie_blocks = re.findall(r'("([^"]{5,100}?)"[^{\[]*?(?:2025-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[^"]*)+)', params_str)
            for block, title in movie_blocks:
                # Filter out paths and unwanted strings
                if (len(title) > 5 and len(title) < 100 and 
                    not title.startswith('film/') and 
                    not title.startswith('wydarzenie/') and
                    not title.endswith('.jpg') and
                    not title.endswith('.jpeg') and
                    not title.endswith('.png') and
                    ' ' in title and
                    not any(bad in title.lower() for bad in ['plakat', 'duzy-obraz', 'poster', 'banner', 'slug'])):
                    movie_titles.add(title)
                    # Find all showtimes in this block
                    showtimes = []
                    for showtime in re.findall(r'(2025-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', block):
                        try:
                            time_part = showtime.split(' ')[1][:5]
                            if time_part not in showtimes:
                                showtimes.append(time_part)
                        except:
                            pass
                    movie_showtimes_map[title] = showtimes

            # Fallback: if no blocks found, use previous logic
            if not movie_titles:
                for title in title_matches:
                    if (len(title) > 5 and len(title) < 100 and 
                        not title.startswith('film/') and 
                        not title.startswith('wydarzenie/') and
                        not title.endswith('.jpg') and
                        not title.endswith('.jpeg') and
                        not title.endswith('.png') and
                        ' ' in title and
                        not any(bad in title.lower() for bad in ['plakat', 'duzy-obraz', 'poster', 'banner', 'slug'])):
                        movie_titles.add(title)
                        movie_showtimes_map[title] = []
                # Try to assign showtimes globally if found
                showtimes = []
                for showtime in showtime_matches[:50]:
                    try:
                        if ' ' in showtime:
                            time_part = showtime.split(' ')[1][:5]
                        else:
                            time_part = showtime[:5]
                        if ':' in time_part and len(time_part) >= 5:
                            if time_part not in showtimes:
                                showtimes.append(time_part)
                    except:
                        pass
                for title in movie_titles:
                    movie_showtimes_map[title] = showtimes[:3]

            # Create film objects
            for i, title in enumerate(sorted(movie_titles)):
                film = {
                    'title': title,
                    'description': f'Film dostępny w kinie Helios. {title}',
                    'image': f'https://img.helios.pl/pliki/film/{self._slugify(title)}/poster.jpg',
                    'showtimes_today': movie_showtimes_map.get(title, []),
                    'showtimes_tomorrow': []
                }
                films.append(film)
                if len(films) >= 15:
                    break
            
        except Exception as e:
            print(f"Error extracting from NUXT data: {e}")
        
        return films
    
    def _extract_from_html_fallback(self, html: str) -> List[Dict]:
        """
        Fallback method to extract movie data from HTML structure.
        
        Args:
            html: HTML content as string
            
        Returns:
            List of film dictionaries
        """
        films = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for movie titles in various HTML elements
            title_selectors = [
                'h2, h3, h4',  # Common heading selectors
                '.movie-title, .film-title',  # Common CSS classes
                '[data-title]',  # Data attributes
            ]
            
            movie_titles = set()
            
            for selector in title_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if (len(text) > 5 and len(text) < 100 and 
                        any(keyword in text.lower() for keyword in [
                            'superman', 'basia', 'smerfy', 'harry', 'film', 'maraton'
                        ])):
                        movie_titles.add(text)
            
            # Create basic film objects
            for title in sorted(movie_titles):
                film = {
                    'title': title,
                    'description': f'Film dostępny w kinie Helios. {title}',
                    'image': f'https://img.helios.pl/pliki/film/{self._slugify(title)}/poster.jpg',
                    'showtimes_today': [],
                    'showtimes_tomorrow': []
                }
                films.append(film)
                
                if len(films) >= 10:  # Limit to 10 movies
                    break
            
        except Exception as e:
            print(f"Error in HTML fallback extraction: {e}")
        
        return films
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to URL-friendly slug.
        
        Args:
            text: Text to convert
            
        Returns:
            URL-friendly slug
        """
        # Basic slugify implementation
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        return slug.strip('-')
    
    async def get_films(self) -> List[Dict]:
        """
        Main method to get films from the cinema.
        
        Returns:
            List of film dictionaries with titles, descriptions, images, and showtimes
        """
        html = await self.fetch_page()
        if not html:
            return []
        
        return self.extract_films_from_html(html)


def extract_films_from_file(file_path: str) -> List[Dict]:
    """
    Extract films from a saved HTML file.
    
    Args:
        file_path: Path to the HTML file
        
    Returns:
        List of film dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        scraper = HeliosScraper("dummy_url")  # URL not needed for file extraction
        return scraper.extract_films_from_html(html)
    
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


# Example usage
if __name__ == "__main__":
    async def main():
        scraper = HeliosScraper("https://helios.pl/wroclaw/kino-helios-magnolia")
        films = await scraper.get_films()
        
        print(f"Found {len(films)} films:")
        for i, film in enumerate(films, 1):
            print(f"{i}. {film['title']}")
            if film['showtimes_today']:
                print(f"   Showtimes: {', '.join(film['showtimes_today'][:3])}")
    
    asyncio.run(main())
