import orm
import pandas as pd
def re_assign_user_ids(old_user_id, new_user_id):
    '''
    When we migrated the auth service, we had to create new user ids for old users.
    The users were not able to reach their past entries.
    This function finds entries by the user, and replaces the user id from the old one to the new one.
    old_user_id and new_user_id are the user ids of the same email address
    '''
    result = orm.Entries.update_many({'user_id':old_user_id}, {'$set':{'user_id':new_user_id}})
    print(f"Updated {result.modified_count} documents")

def find_old_user_id(keyword):
    '''
    if we don't need the old user id, but know some key words, we can find
    the user id by searching for the keyword
    '''
    def has_keyword(chat_list, keyword):
        for chat_dict in chat_list:
            for value in chat_dict.values():
                if isinstance(value, str) and keyword in value:
                    return True
        return False
    
    entries = pd.json_normalize(orm.Entries.find({}, {'_id':1, 'chats':1, 'user_id':1}))
    entries = entries[entries['chats'].apply(lambda x: has_keyword(x, keyword))]
    print('the matched user_ids')
    print(entries['user_id'].unique())


