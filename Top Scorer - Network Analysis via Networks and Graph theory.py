#!/usr/bin/env python
# coding: utf-8

# # Top Scorer - Network Analysis via Networks and Graph theory

# <b>Summary:</b> We used networks and graph theory to understand the relationship between each ticket submitted. With this, we managed to map the unlinked customer 100% either via the phone number, email address or order id.

# <b>Problem Statement:</b>
# Customers can contact customer service via various channels such as the livechat function, filling up certain forms or calling in for help. Each time a customer contacts us with a new contact method, a new ticket is automatically generated. A complication arises when the same customer contacts us using different phone numbers or email addresses resulting in multiple tickets for the same issue. Hence, our challenge here is to identify how to merge relevant tickets together to create a complete picture of the customer issue and ultimately determine the RCR

# <b>Dataset: </b>
# You can download the dataset from https://www.kaggle.com/c/scl-2021-da/data

# <b>Solution: </b>
# The solution is simple and sweet, with minor cleaning and used basic network to map out the relationship between each ticket and we managed to formulate the solution and map out the customer network 100% within the timelimit.

# ### First we load the dataset
Each Order ID represents a transaction in Shopee.
Each Id represents the Ticket Id made to Shopee Customer Service.
All Phone Numbers are stored without the country code and the country code can be ignored.
Contacts represent the number of times a user reached out to us in that particular ticket (Email, Call, Livechat etc.)
If a value is NA means that the system or agent has no record of that value.
# In[1]:


import pandas as pd
import networkx as nx


# In[2]:


df = pd.read_json('dataset/contacts.json')
df


# ## Data Cleaning
# Data cleaning is the mandatory step before any modeling. 
# We append "Email_ " , "Phone_" and "OrderId_"  to help us identify the data type later on.

# In[3]:


df.Email = df.Email.apply(lambda x: "Email_"+x if x !='' else '')
df.Phone = df.Phone.apply(lambda x: "Phone_"+x if x !='' else '')
df.OrderId = df.OrderId.apply(lambda x: "OrderId_"+x if x !='' else '')
df


# ## Creating the Graph network
# <b>1. Create the nodes with Id and with attributes as Contacts </b>

# In[4]:


# Create the nodes with Id & Contacts

nodes = []

for _,Id,_,_,Contacts,_ in df.itertuples():
    nodes.append((Id,{"Contacts": Contacts}))


# In[5]:


# Add the nodes into the new graph G

G = nx.Graph()
G.add_nodes_from(nodes)


# In[6]:


# Now that we have 500000 nodes, 0 edges
G.number_of_nodes(), G.number_of_edges()


# <b>2. Create the edges between: Id ↔ Email, Id ↔ Phone, Id ↔ OrderId</b>
# 
# And the nodes of Email, Phone & OrderId are auto created in the process.

# In[ ]:


# Create the edges between: Id ↔ Email, Id ↔ Phone, Id ↔ OrderId

G.add_edges_from(df[df.Email != ''][['Id', 'Email']].to_records(index=False))
G.add_edges_from(df[df.Phone != ''][['Id', 'Phone']].to_records(index=False))
G.add_edges_from(df[df.OrderId != ''][['Id', 'OrderId']].to_records(index=False))


# In[ ]:


G.number_of_nodes(), G.number_of_edges()


# <b>3. List down the connected component.</b> 
# 
# Each list contains 1 connected component

# In[ ]:


# List down the connected component

conn_comp = list(nx.connected_components(G))
conn_comp


# ## Extract the graph network 
# The idea is one ticket_id one line, with their connected ticket id concated, number of contact points made summed up.
# 
# For each connected component, i.e. each list, we concated the ticket_id within, and summed up the contact made (stored under the nodes attributes earlier)

# In[ ]:


output = []

# for each connected component, i.e. each list, we apended the ticket_id within (to concat in the later part)

for each_connected_component in conn_comp:
    
    id_list = []

    for each_node in each_connected_component:
        
        # check if the node is a number, append to the id_list
        
        if str(each_node).isnumeric():

            id_list.append(each_node)

    sum_of_contacts = 0
    
    for order_id in id_list:
        
        # summed up the attributes ie. contact made that belongs to the node
        
        sum_of_contacts += G.nodes[order_id]['Contacts']

    output_str = '-'.join([str(each_node) for each_node in sorted(id_list)]) + ', '  + str(sum_of_contacts)
    for order_id in id_list:

        output.append([order_id, output_str])


# Convert the output as dataframe, and sorted according to the competition requirement, and exported as csv file.

# In[ ]:


output_final = pd.DataFrame(output)
output_final= output_final.rename(columns={0:'ticket_id', 1:'ticket_trace/contact'})


# In[ ]:


output_final.sort_values('ticket_id').to_csv('output.csv', index=False)

