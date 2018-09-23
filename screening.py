import pandas as pd
import numpy as np
np.set_printoptions(suppress=True)
import vptree
from geopy.distance import great_circle

def generate_points(df_ships):
    '''
    Takes in a dataframe of ship data and uses MMSI, Latitude, and Longitude fields
    in order to tuen them into points that can be passed to the vantage tree function.
    '''
    points = tuple(zip(df_ships.MMSI, df_ships.LAT, df_ships.LON))
    return points

def get_distance_in_meters(point1, point2):
    '''
    Returns the distance in meters between two points.
    '''
    p1_lat_lon = (point1[1], point1[2])
    p2_lat_lon = (point2[1], point2[2])
    return great_circle(p1_lat_lon, p2_lat_lon).m

def generate_vantage_point_tree(points):
    '''
    INPUTS:
    points: An array of tuples representing ship positions. Each tuple is of the form
            (ship's MMSI, ship's latitude, ship's longitude).
    OUTPUT: A vantage point tree data structure that can be used to easily query ships within a given distance of another ship.
    '''    
    tree = vptree.VPTree(points, get_distance_in_meters)
    return tree

def get_potential_interaction_pairs(points, tree, distance_in_m=7315):
    '''
    INPUTS:
    points: An array of tuples that contain ship MMSI, ship LAT, and ship LON.
    tree: The vantage point tree used to search for ships within range of a given ship position.
    distance_in_m: Distance in meters. Ships within this distance of eachother will count as a potential interaction.
    
    OUTPUT:
    Return none if there are no potential interactions. Else return a list of tuples containing the MMSI identifiers
    of ships that could be interacting.
    '''
    
    interacting_MMSI_pairs = []
    for ship in points:
        original_ship_MMSI = int(ship[0])
        interacting_ship_MMSI = set()
        interactions_for_one_ship = tree.get_all_in_range(ship, distance_in_m)
        # If statement makes sure we don't just have the original ship near itself.
        if len(interactions_for_one_ship) > 1:
            for interaction in interactions_for_one_ship:
                interacting_ship_MMSI.add(int(interaction[1][0]))
            # Ensure the original ship MMSI isn't included as an interacting ship.    
            interacting_ship_MMSI.discard(original_ship_MMSI)
            pairs = [(original_ship_MMSI, MMSI) for MMSI in interacting_ship_MMSI]

            for pair in pairs:
                reversed_pair = tuple(reversed(pair))
                if (pair not in interacting_MMSI_pairs) and (reversed_pair not in interacting_MMSI_pairs):
                    interacting_MMSI_pairs.append(pair)
                
    if len(interacting_MMSI_pairs) > 1:
        return interacting_MMSI_pairs
    else:
        return None
        