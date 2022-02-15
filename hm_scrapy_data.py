# Imports
import re
import os
import sqlite3
import logging
import requests
import numpy    as np
import pandas   as pd
from bs4        import BeautifulSoup
from datetime   import datetime
from sqlalchemy import create_engine

# Data Collection
def data_collection(url, headers):

    # Request to URL
    page = requests.get( url, headers=headers)

    # Beutiful Soup Object
    soup = BeautifulSoup(page.text, 'html.parser')

    # ==================== Product Data ========================e
    products = soup.find( 'ul', class_='products-listing small')
    product_list = products.find_all('article', class_='hm-product-item')

    # Product ID
    product_id = [p.get( 'data-articlecode' ) for p in product_list]

    # Product Category
    product_category = [p.get( 'data-category' ) for p in product_list]

    # Product Name
    product_list = products.find_all('a', class_='link')
    product_name= [p.get_text('data-category') for p in product_list]

    # Product Price
    product_list = products.find_all('span', class_='price regular')
    product_price = [p.get_text('price regular') for p in product_list]

    # DataFrame Definition
    data = pd.DataFrame([product_id, product_category, product_name, product_price]).T
    data.columns = ['product_id','product_category','product_name','product_price']
    return(data)

# Data Collection by Products
def data_collection_by_product(data, headers):

    # empty dataframe
    df_compositions = pd.DataFrame()

    # unique columns for all products
    aux = []

    df_pattern = pd.DataFrame( columns=['Art. No.', 'Composition', 'Fit', 'Size', 'More sustainable materials', 'Product safety'] )

    for i in range(  len(data) ):
        # API Requests
        
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id']+ '.html'
        logger.debug( 'Product: %s', url )
        
        page = requests.get( url, headers=headers )
        
        # Beautiful Soup object
        soup = BeautifulSoup( page.text, 'html.parser' )

        # ==================== color name =================================
        product_list = soup.find_all( 'a', class_='filter-option miniature active' ) + soup.find_all( 'a', class_='filter-option miniature' )
        color_name = [p.get( 'data-color' ) for p in product_list]

        # product id
        product_id = [p.get( 'data-articlecode' ) for p in product_list]
        df_color = pd.DataFrame( [product_id, color_name] ).T
        df_color.columns = ['product_id', 'color_name']
        
        for j in range(len( df_color )):
            
            # API Requests
            url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id']+ '.html'
            logger.debug( 'Color: %s', url )

            page = requests.get( url, headers=headers )
            
            # Beutiful Soup Object
            soup = BeautifulSoup( page.text, 'html.parser' )
            
            # ==================== Product Name ====================
            product_name = soup.find_all( 'h1', class_='primary product-item-headline' )
            product_name = product_name[0].get_text()
            
            # ==================== Product Price ====================
            product_price = soup.find_all( 'div', class_='primary-row product-item-price' )
            product_price = re.findall( r'\d+\.?\d+', product_price[0].get_text())[0]
                
            # ==================== composition =================================
            product_composition_list = soup.find_all( 'div', class_='pdp-description-list-item' )
            product_composition = [list( filter( None, p.get_text().split( '\n' ) ) ) for p in product_composition_list]

            # reaname dataframe
            df_composition = pd.DataFrame( product_composition ).T
            df_composition.columns = df_composition.iloc[0]

            # delete first row
            df_composition = df_composition.iloc[1:].fillna( method='ffill' )
            
            # Remove pocket lining, shell and lining
            df_composition['Composition'] = df_composition['Composition'].replace( 'Pocket lining:','', regex=True)
            df_composition['Composition'] = df_composition['Composition'].replace( 'Shell:','', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace( 'Lining:','', regex=True)
            df_composition['Composition'] = df_composition['Composition'].str.replace( 'Pocket:','', regex=True)

            # Garantee the same number of columns
            df_composition = pd.concat( [df_pattern, df_composition],axis=0 )

            # Rename Columns
            df_composition.columns = ['product_id', 'composition', 'fit', 'size', 'more_sustainable_materials', 'product_safety']
            df_composition['product_name'] = product_name
            df_composition['product_price'] = product_price

            # Keep new columns if it shows up
            aux = aux + df_composition.columns.tolist()

            # merge data color + decomposition
            df_composition = pd.merge( df_composition, df_color, how='left', on='product_id' )          

            # all products
            df_compositions = pd.concat( [df_compositions, df_composition], axis=0 ) 

    # Joi Showroom data + details
    df_compositions['style_id'] = df_compositions['product_id'].apply( lambda x: x[:-3] )
    df_compositions['color_id'] = df_compositions['product_id'].apply( lambda x: x[-3:] )

    # Scrapy Date
    df_compositions['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return (df_compositions)

# Data Cleaning
def data_cleaning( data_product ):

    # Product ID
    df_data = data_product.dropna( subset=['product_id'] )

    # Product Name data set
    df_data['product_name'] = df_data['product_name'].str.replace( '\n','' )
    df_data['product_name'] = df_data['product_name'].str.replace( '\t','' )
    df_data['product_name'] = df_data['product_name'].str.replace( '  ','' )
    df_data['product_name'] = df_data['product_name'].str.replace( ' ','_' ).str.lower()

    # Product Fit data set
    df_data['fit'] = df_data['fit'].apply( lambda x: x.replace( ' ','_' ).lower() if pd.notnull( x ) else x )

    # Color name
    df_data['color_name'] = df_data['color_name'].apply( lambda x: x.replace( ' ','_' ).lower() if pd.notnull( x ) else x )

    # Select the size
    df_data['size_number'] = df_data['size'].apply( lambda x: re.search('\d{3}cm', x).group(0) if pd.notnull( x ) else x )
    df_data['size_number'] = df_data['size_number'].apply( lambda x: re.search('\d+', x).group(0) if pd.notnull( x ) else x)
    df_data['size_model'] = df_data['size'].str.extract('(\d+/\\d+)') 

    # ===================== Composition =========================

    # Break composition by comma
    df1 = df_data['composition'].str.split( ',', expand=True ).reset_index(drop=True)

    # cotton | Spandex | elasterell
    df_ref = pd.DataFrame(columns=['cotton','spandex','polyester'])

    # cotton
    df_cotton_0 = df1.loc[df1[0].str.contains( 'Cotton', na=True), 0]
    df_cotton_0.name = 'cotton'

    df_cotton_1 = df1.loc[df1[1].str.contains( 'Cotton', na=True ), 1]
    df_cotton_1.name = 'cotton'

    # combine
    df_cotton = df_cotton_0.combine_first( df_cotton_1 )
    df_ref = pd.concat( [df_ref, df_cotton ], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last')]

    # Spandex
    df_spandex_1 = df1.loc[df1[1].str.contains( 'Spandex', na=True ), 1]
    df_spandex_1.name = 'spandex'

    # combine
    df_ref = pd.concat( [df_ref, df_spandex_1 ], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last')]

    # polyester
    df_polyester_0 = df1.loc[df1[0].str.contains( 'Polyester', na=True ), 0]
    df_polyester_0.name = 'polyester'

    # combine
    df_ref = pd.concat( [df_ref, df_polyester_0], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]

    # join of combine with product_id
    df_aux = pd.concat( [df_data['product_id'].reset_index(drop=True), df_ref], axis=1 )

    # format composition data
    df_aux['cotton'] = df_aux['cotton'].apply( lambda x: int( re.search( '\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['spandex'] = df_aux['spandex'].apply( lambda x: int( re.search( '\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['polyester'] = df_aux['polyester'].apply( lambda x: int( re.search( '\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )

    # final join
    df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0)
    df_data = pd.merge( df_data, df_aux, on='product_id', how='left')

    # drop columns
    df_data = df_data.drop( columns = ['size','composition','more_sustainable_materials', 'product_safety'], axis=1)

    # drop duplicates
    df_data = df_data.drop_duplicates()
    return(df_data)

# Data Insert
def data_insertion(df_data):

    data_insert = df_data[[
        'product_id',       
        'style_id',
        'color_id',
        'product_name',
        'product_price',
        'color_name',
        'size_number',
        'size_model',
        'fit',
        'cotton',
        'spandex',
        'polyester',   
        'scrapy_datetime'
    ]]

    # create database connection
    conn = create_engine('sqlite:////home/rengineer/Documentos/DS/ds_ao_dev/Modulo_8/venv/database_hm.sqlite', echo=False)

    # data insert
    data_insert.to_sql( 'vitrine_hm', con=conn, if_exists='append', index=False )
    
    return(None)

if __name__ == '__main__':
    # Loggin
    path = '/home/rengineer/Documentos/DS/ds_ao_dev/Modulo_8/venv/'

    if not os.path.exists( path + 'Logs' ):
        os.makedirs(path + 'Logs')

    logging.basicConfig(
        filename = path + 'Logs/hm_scrapy_data.log',
        level = logging.DEBUG,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger('hm_scrapy')

    # Parameters & Constants
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    # URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'

    # Data Collection
    data = data_collection(url, headers)
    logger.info('Data collect done')

    # Data Collection by product
    data_product = data_collection_by_product(data, headers)
    logger.info('Data collect by product done')

    # Data Cleaning
    data_product_cleaning = data_cleaning(data_product)
    logger.info('Data cleaning done')

    # Data Insertion
    data_insertion(data_product_cleaning)
    logger.info('Data insertion done')