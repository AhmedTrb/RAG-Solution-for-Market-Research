configurations = {
    'amazon': {
        'MAX_PAGES': 1,
        'base_url': "https://www.amazon.com",
        'start_url': "https://www.amazon.com/s?k={query}",
        
        'URL_EXTRACTION_CONFIG': {
            'product_container': {  
                'tag': 'div',
                'attrs': {'data-component-type': 's-search-result'}
            },
            'product_link': { 
                'tag': 'a',
                'attrs': {'class': 'a-link-normal s-no-outline'}
            },
            'url_cleanup': True 
        },

        'DETAILS_EXTRACTION_CONFIG': {
            'fields': {
                'Title': {
                    'selector': 'span',
                    'attrs': {'id': 'productTitle'},
                    'processing': lambda x: x.text.strip()
                },
                'Price': {
                    'selector': 'span',
                    'attrs': {'class': 'a-offscreen'},
                    'processing': lambda x: x.text.strip()
                },
                'Description': {
                    'selector': 'div#productDescription',
                    'processing': lambda x: ' '.join([p.text.strip() for p in x.select('p')]) if x else 'N/A'
                },
                'Rating': {
                    'selector': 'span.a-icon-alt',
                    'processing': lambda x: x.text.split()[0] if x else 'N/A'
                },
                'Review Count': {
                    'selector': 'span#acrCustomerReviewText',
                    'processing': lambda x: x.text.split()[0] if x else 'N/A'
                },
                'review_title': {
                'selector': 'a',
                'attrs': {'data-hook': 'review-title'},
                'processing': lambda x: x.text if x else 'N/A'
            },
            'review_date': {
                'selector': 'span',
                'attrs': {'data-hook': 'review-date'},
                'processing': lambda x: x.text if x else 'N/A'
            },
            'review_text': {
                'selector': 'span',
                'attrs': {'data-hook': 'review-body'},
                'processing': lambda x: x.text if x else 'N/A'
            }
            },
            'default_value': 'N/A'
        },

        'PAGINATION_CONFIG': {
            'next_page': {
                'selector': 'a',
                'attrs': {'class': 's-pagination-next'},
                'enabled': True  
            }
        }
    },

    'bestbuytunisie': {
        'MAX_PAGES': 0,
        'base_url': "https://bestbuytunisie.tn",
        'start_url': "https://bestbuytunisie.tn/?s={query}",
        
        'URL_EXTRACTION_CONFIG': {
            'product_container': {
                'tag': 'div',
                'attrs': {'class': 'xts-col'}
            },
            'product_link': {
                'tag': 'a',
                'attrs': {'class': 'xts-post-link xts-fill'}
            },
            'url_cleanup': True
        },

        'DETAILS_EXTRACTION_CONFIG': {
            'fields': {
                'Title': {
                    'selector': 'h1',
                    'attrs': {'class': 'product_title entry-title'},
                    'processing': lambda x: x.text.strip()
                },
                'Price': {
                    'selector': 'p',
                    'attrs': {'class': 'price'},
                    'processing': lambda x: x.text.strip()
                },
                'Description': {
                    'selector': 'div.woocommerce-product-details__short-description',
                    'processing': lambda x: x.text.strip() if x else 'N/A'
                }
            },
            'default_value': 'N/A'
        },

        'PAGINATION_CONFIG': {
            'next_page': {
                'selector': 'a',
                'attrs': {'class': 'page-numbers'},
                'enabled': True
            }
        }
    },

    'ebay': {
        'MAX_PAGES': 0,
        'base_url': "https://www.ebay.fr",
        'start_url': "https://www.ebay.fr/sch/353/bn_16573761/i.html?_nkw={query}",

        'URL_EXTRACTION_CONFIG': {
            'product_container': {
                'tag': 'div',
                'attrs': {'class': 's-item__wrapper'}
            },
            'product_link': {
                'tag': 'a',
                'attrs': {'class': 's-item__link'}
            },
            'url_cleanup': True
        },

        'DETAILS_EXTRACTION_CONFIG': {
            'fields': {
                'Title': {
                    'selector': 'h1',
                    'attrs': {'class': 'x-item-title__mainTitle'},
                    'processing': lambda x: x.text.strip() if x else 'N/A'
                },
                'Price': {
                    'selector': 'div',
                    'attrs': {'class': 'x-price-primary'},
                    'processing': lambda x: x.text.strip() if x else 'N/A'
                },
                'Description': {
                    'selector': 'div',
                    'attrs': {'class': 'vim x-about-this-item'},
                    'processing': lambda x: ' '.join(x.stripped_strings) if x else 'N/A'
                },
                'Seller Name': {
                    'selector': 'h2',
                    'attrs': {'class': 'x-store-information__store-name'},
                    'processing': lambda x: x.text.strip() if x else 'N/A'
                },
                'comment': {
                    'selector': 'div',
                    'attrs': {'class': 'fdbk-container__details__comment'},
                    'processing': lambda x: x.text.strip() if x else 'N/A'
                }
            },
            'default_value': 'N/A'
        },

        'PAGINATION_CONFIG': {
            'next_page': {
                'selector': 'a',
                'attrs': {'class': 'pagination__next'},
                'enabled': True
            }
        }
    },

    'newegg': {
        'MAX_PAGES': 0,
        

        'base_url': "https://www.newegg.com/",
        'start_url': "https://www.newegg.com/p/pl?d={query}",

        'URL_EXTRACTION_CONFIG': {
            'product_container': {
                'tag': 'div',
                'attrs': {'class': 'item-cell'}
            },
            'product_link': {
                'tag': 'a',
                'attrs': {'class': 'item-img'}
            },
            'url_cleanup': True
        },

        'DETAILS_EXTRACTION_CONFIG': {
            'fields': {
                'Title': {
                    'selector': 'h1',
                    'attrs': {'class': 'product-title'},
                    'processing': lambda x: x.text.strip()
                },
                'Price': {
                    'selector': 'div',
                    'attrs': {'class': 'price-current'},
                    'processing': lambda x: x.text.strip()
                },
                'Description': {
                    'selector': 'div.product-bullets',
                    'processing': lambda x: x.text.strip()
                },
                'Rating': {
                    'selector': 'i',
                    'attrs': {'class': 'rating'},
                    'processing': lambda x: x.get('title', 'N/A') if x else 'N/A'
                },
                'Review Count': {
                    'selector': 'div.product-rating',
                    'processing': lambda x: x.text.split()[0] if x else 'N/A'
                },
                'comment': {
                    'selector': 'div',
                    'attrs': {'class': 'comments-cell-body'},
                    'processing': lambda x: x.text.strip()
                }
            },
            'default_value': 'N/A'
        },
        'PAGINATION_CONFIG': {
            'next_page': {
                'selector': 'a',
                'attrs': {'class': 'btn'},
                'enabled': True
            }
        }
    }
}