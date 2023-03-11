import requests, json
import pandas as pd

class RedditLoader:
    '''
        Class to download data from reddit

        Parameters
        ----------
        path: str
            Path to json file containing credentials
        
        Attributes
        ----------
        config: dict
            Dictionary containing credentials for reddit API
        headers: dict
            Dictionary containing headers for reddit API

        Methods
        -------
        get_token() -> str
            Get token from reddit API
        get_single_batch(subreddit:str, sort_by:str, limit:int, before: str=None) -> list[list]
            Get a single batch of data from reddit API
        get_all_data(subreddit:str, sort_by:str) -> pd.DataFrame
            Get all data from reddit API
    '''
    def __init__(self, path:str):
        with open(path) as f:
            self.config = json.load(f)
        self.headers = {'User-Agent': 'MyBot/0.0.1'}
        self.headers['Authorization'] = 'bearer ' + self.get_token()

        if requests.get('https://oauth.reddit.com/api/v1/me', headers=self.headers).status_code == 200:
            print('Success authenticated')


    def get_token(self) -> str:
        '''
            Get token from reddit API

            Returns
            -------
            str
                Token for reddit API
        '''
        auth = requests.auth.HTTPBasicAuth(self.config['client_id'], self.config['secret_token'])
        data = {'grant_type': 'password',
                'username': self.config['username'],
                'password': self.config['password']
        }

        headers = self.headers
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)
        
        try:
            return res.json()['access_token']
        except KeyError:
            print(res.json())
            raise Exception('Invalid credentials')
        

    def get_single_batch_post_from_reddit(self, subreddit:str, sort_by:str, limit, before: str=None) -> list[list]:
        '''
            Get a single batch of data from reddit API

            args:
            ---------
            subreddit: str
                Subreddit to get data from
            sort_by: str
                How to sort the data
            limit: int
                Number of posts to get
            before: str
                Name of post to get data before
            
            Returns
            -------
            list[list]
                List of lists containing name, title, and selftext of each post
        '''
        # Set up the parameters
        uri = f'https://oauth.reddit.com/r/{subreddit}/{sort_by}'
        params = {'limit': limit, 'raw_json': 1}
        if before:
            params['before'] = before

        # Make request to reddit API
        res = requests.get(uri, headers=self.headers, params=params)
        raw_data = res.json()

        # Get name, title, and selftext from each post
        data = []
        for post in raw_data['data']['children']:
            data.append([post['data']['name'], post['data']['title'], post['data']['selftext']])


        return data
    
    def get_single_batch_post_comment_from_reddit(self, subreddit:str, sort_by:str, limit:int, before: str=None) -> list[list]:
        '''
            Get a single batch of data from reddit API

            args:
            ---------
            subreddit: str
                Subreddit to get data from
            sort_by: str
                How to sort the comments
            limit: int
                Number of posts to get
            before: str
                Name of post to get data before
            
            Returns
            -------
            list[list]
                List of lists containing name, title, and selftext of each post
        '''
        # Set up the parameters
        uri = f'https://oauth.reddit.com/r/{subreddit}/top'
        params = {'limit': limit, 'raw_json': 1, 't': 'all'}
        if before:
            params['before'] = before

        # Make request to reddit API
        res = requests.get(uri, headers=self.headers, params=params)
        raw_data = res.json()

        # Get top 5 comments for each post
        data = []
        for post in raw_data['data']['children']:
            post_name = post['data']['name']
            post_title = post['data']['title']
            post_id = post['data']['id']

            # Get comments
            uri = f'https://oauth.reddit.com/comments/{post_id}'
            params = {'limit': 5, 'raw_json': 1, 'sort': sort_by}
            res = requests.get(uri, headers=self.headers, params=params)
            raw_comments = res.json()

            # Add post name, post title, and comment text to data
            # print(raw_comments)
            for comment in raw_comments[1]['data']['children']:
                if 'body' in comment['data']:
                    data.append([post_name, post_title, comment['data']['body']])
        return data

    def get_all_data(self, type:str, subreddit:str, sort_by:str, verbose:bool=False) -> pd.DataFrame:
        '''
            Get all data from reddit API

            args:
            ---------
            type: str
                Whether to get posts or comments
            subreddit: str
                Subreddit to get data from
            sort_by: str
                How to sort the data
            verbose: bool
                Whether to print progress

            Returns
            -------
            pd.DataFrame
                Dataframe containing name, title, and selftext of each post
        '''
        if type == 'post':
            get_data = self.get_single_batch_post_from_reddit
        elif type == 'comment':
            get_data = self.get_single_batch_post_comment_from_reddit
        else:
            raise Exception('Invalid type')
        data = []
        before = None
        if verbose:
            print('Getting data...')
            batch = 0
        data_size = 0
        while True:
            try:
                data += get_data(subreddit, sort_by, 100, before)
                before = data[-1][0]

                if verbose:
                    batch += 1
                    print(f'Batch {batch} complete, loaded {len(data)} posts.')
                if len(data) == data_size:
                    break
                data_size = len(data)
            except Exception as e:
                print(e)
                break

        return RedditLoader.make_dataframe(type, data)
    
    def save_data(self, type:str, subreddit:str, sort_by:str, path:str, verbose:bool=False):
        '''
            Save data from reddit API to csv

            args:
            ---------
            type: str
                Whether to get posts or comments
            subreddit: str
                Subreddit to get data from
            sort_by: str
                How to sort the data
            path: str
                Path to save data to
            verbose: bool
                Whether to print progress
        '''
        df = self.get_all_data(type, subreddit, sort_by, verbose=verbose)
        df.to_csv(path, index=False)

    @staticmethod
    def make_dataframe(type:str, data:list[list]) -> pd.DataFrame:
        if type == 'post':
            return pd.DataFrame(data, columns=['name', 'title', 'text'])
        elif type == 'comment':
            return pd.DataFrame(data, columns=['name', 'title', 'comment'])
        else:
            raise Exception('Invalid type')
        
if __name__ == '__main__':
    loader = RedditLoader('reddit_cred.json')
    loader.save_data('comment', 'askreddit', 'controversial', 'askreddit.csv', verbose=True)
    