#!/usr/bin/env python
'''
Shopping Helper

Given a list of store inventories and a shopping list, return the minimum number of
store visits required to satisfy the shopping list.

For example, given the following stores & shopping list:

  Shopping List: 10 apples, 4 pears, 3 avocados, 1 peach

  Kroger: 4 apples, 5 pears, 10 peaches
  CostCo: 3 oranges, 4 apples, 4 pears, 3 avocados
  ALDI: 1 avocado, 10 apples
  Meijer: 2 apples

The minimum number of stores to satisfy this shopping list would be 3:
Kroger, CostCo and ALDI.
or
Kroger, CostCo and Meijer.

Shopping lists and store inventories will be passed in JSON format,
an example of which will be attached in the email.  Sample outputs for the
given inputs should also be attached as well.

Use the helper provided to print.

Usage: shopping_helper.py (shopping_list.json) (inventories.json)



                            NOTES

*************************IMPORTANT*************************

I implemented an algorithm that uses a greedy heuristic,
inspired by the branch and bound algorithm.
The greedy heuristic is just an estimate. It is not optimal in all cases. 

I wanted to implement the branch and bound algorithm for this problem.

However, I wanted to respect the two hour frame for completing this coding challenge,
so I did not implement branch and bound algorithm since this problem is very similar
to the traveling sales person problem. I utilized significant numbers of permutations
to obtain the sample output. However, if I had more time, I would have used my greedy
heuristic to find the upper bound for this problem. I would have had to find a way to 
estimate the lower bound for each branch in the "promising" function,
but other than that, the algorithm would use recursion to find each permutation and
consider pruning at stage of the permutation.

-----------------------MISC-----------------------
planning/initial thoughts:
what if there are enough apples at two stores, but not separately (one store or the other)
    keep track of running uncovered inventory by quanity

greedy heuristic: 
while shopping list is not empty:
    find shop that covers the most
    add that shop to shop set and delete found elements from shopping list (via quanity, not just checkbox)
return shop list

'''





import argparse
import copy
import json
import sys


def inventory_score(shopping_list, total_inventory):
    sum = 0
    for item in shopping_list:
        #item score = desired amount - inventory amount (potentially 0, hence the else)
        if item in total_inventory:
            item_score =  shopping_list[item] - total_inventory[item]
        else:
            item_score = shopping_list[item]
        if item_score > 0: #add penalty to sum score if not covered
            sum += item_score
        #otherwise, do not add penalty to sum score
    return sum
    
#returns true/false to see if there is enough inventory for all
def proper_inventory(shopping_list, inventory):
    total_inventory = {}
    #check each store, and its items, and add those to total inventory
    for shop in inventory["stores"]:
        for item in shop["inventory"]:
            #add or start new key with value of the inventory of curr item
            if item in total_inventory:
                total_inventory[item] += shop["inventory"][item]
            else:
                total_inventory[item] = shop["inventory"][item]

    score = inventory_score(shopping_list, total_inventory)
    return score <= 0 # returns true if shopping list
    # is at least fully covered by inventory

#returns score of store in terms of how well it covers the shopping list. the lower the score, the better
# a score of 0 or less means the store has the ability to cover all or more than what is in the shopping list.
def shop_score(shop, shopping_list):
    sum = 0
    for item in shopping_list:
        #item score = desired amount - inventory amount (potentially 0, hence the else)
        if item in shop["inventory"]:
            item_score = shopping_list[item] - shop["inventory"][item]
        else:
            item_score = shopping_list[item]
        if item_score > 0: #if not fully covered, add penalty to score sum
            sum += item_score
        #otherwise, do not add penalty to score sum
    return sum

#find the store at the current moment (greedy) for best coverage of 
# current version of shopping list
def find_best(shopping_list, inventory):
    best_num = 0
    best_score = sys.maxsize
    for i, shop in enumerate(inventory["stores"]):
        score = shop_score(shop, shopping_list)
        if score < best_score:
            best_score = score
            best_num = i
    return best_num


#shopping list is to buy list; inventory is list of shops
def greedy_heuristic(shopping_list, inventory):
    trip = [] #stores final shop list
    while shopping_list: #while shopping/to buy list not empty (not all "checked")
        #get shop number of shop that covers the shopping (to buy) list 
        #the most out of all in the current inventory.
        #Also, update the shopping list to not include items purchased at this shop
        shop_num = find_best(shopping_list, inventory)

        #access best shop via shop number
        curr_shop = inventory["stores"][shop_num]
        
        #remove shopping list items that are covered by this shop
        for item in curr_shop["inventory"]:
            if item in shopping_list:
                shopping_list[item] -= curr_shop["inventory"][item]
                if shopping_list[item] <= 0:
                    shopping_list.pop(item)

        #add best shop to final shop list
        trip.append(curr_shop["name"])

        #delete best store from inventory so not considered in future
        inventory["stores"].pop(shop_num)

    return trip

#manually makes deep copy of dict since copy module does not offer that
def copy_shopping_list(shopping_list_json):
    shopping_list_copy = {}
    for key in shopping_list_json:
        shopping_list_copy.update({key : shopping_list_json[key]})
    return shopping_list_copy

#make deep copy of list and put it in wrapper dict
def copy_inventory(inventory_json):
    inventory_list_copy = copy.deepcopy(inventory_json["stores"])
    inventory_copy = {"stores" : inventory_list_copy}
    return inventory_copy

#because lists are not hashable in sets, must manually remove list copies in list of lists
def remove_copies(trip_list):
    copyless = []
    [copyless.append(trip) for trip in trip_list if trip not in copyless]
    return copyless    

# to help you get started, we have provided some boiler plate code
def satisfy_shopping_list(shopping_list_json, inventory_json):
    # find out minimum combination of stores that would satisfy shopping list

    # if shopping list is impossible to satisfy
    shopping_list_satisfiable = proper_inventory(shopping_list_json, inventory_json)
    if shopping_list_satisfiable:
        # print out number of stores and corresponding combinations
        # num_stores = 0
        # print "The shopping list can be satisfied by visiting {} store(s):".format(num_stores)
        # for each valid store_combination:
        # print_store_list(store_combination)
        
        #because delete from inventory/shopping list, need copies since
        # mutable data structures as arguments are passed by ref
        inventory_copy = copy_inventory(inventory_json)
        shopping_list_copy = copy_shopping_list(shopping_list_json)
        
        #initial greedy heuristic solution
        trip = greedy_heuristic(shopping_list_copy, inventory_copy)
        min_trip = len(trip) #effectively an upper bound solution
        new_min_trip = min_trip #copy meant to be written over later

        #container for all possible solutions
        all_trips = [trip]
        for x in range(len(inventory_json["stores"])):
            #move first store to last place in stores list
            inventory_json["stores"].append(inventory_json["stores"][0])
            inventory_json["stores"].pop(0)
            
            #create copies again for same reason when finding more versions of solution
            inventory_copy = copy_inventory(inventory_json)
            shopping_list_copy = copy_shopping_list(shopping_list_json)

            #run greedy algorithm with this version of inventory (stores list)
            # and if it is just as optimal, then add to list of possible trips
            curr_trip = greedy_heuristic(shopping_list_copy, inventory_copy)

            #if curr solution is better than upper bound, keep
            if(len(curr_trip) <= min_trip):
                all_trips.append(curr_trip)
                #just in case greedy first time was not optimal
                new_min_trip = len(curr_trip)
        
        #to get rid of duplicate solutions in this pseudo branch and bound algorithm
        all_trips = remove_copies(all_trips)
        all_trips.sort() #alphabetical order relative to start of each trip

        print("The shopping list can be satisfied by visting {} store(s):".format(new_min_trip))
        for my_trip in all_trips: 
            print_store_combination(my_trip)
    else:
        print("No combination of given stores can satisfy this shopping list :(")

def print_store_combination(store_combination):
    '''
    Print store combination in the desired format.

    Args:
        store_combination: store list to print
        type: list of str
    '''
    store_combination_copy = copy.deepcopy(store_combination)
    store_combination_copy.sort()
    print(', '.join(store_combination_copy))


def main():
    args = parse_args()
    with open(args.shopping_list_json_path) as shopping_list_json_file, open(args.inventory_json_path) as inventory_json_file:
        shopping_list_json = json.load(shopping_list_json_file)
        inventory_json = json.load(inventory_json_file)
        satisfy_shopping_list(shopping_list_json, inventory_json)


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('shopping_list_json_path')
    p.add_argument('inventory_json_path')

    args = p.parse_args()
    return args

if __name__ == '__main__':
    main()
