import louvain
import igraph as ig
import pandas as pd
import numpy as np
import os

#%% Set input and output directories
data_dir = '../data/'
result_dir = '../results/'; 

output_dir = result_dir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#%% Read data
print('Reading network')
edge_orig_df = pd.read_stata(data_dir + 'dependence.dta', preserve_dtypes=False)
cols = ['ccode1', 'ccode2', 'depabgled', 'depbagled', 'year']

#%% Create edges
edge_df = edge_orig_df.loc[pd.notnull(edge_orig_df['depabgled']) & edge_orig_df['depabgled'] > 0,
                          ['ccode1', 'ccode2', 'depabgled', 'year']]
edge_df['weight'] = edge_df['depabgled']
del edge_df['depabgled']

# Create edges in other direction
edge_rev_df = edge_orig_df.loc[pd.notnull(edge_orig_df['depabgled']) & edge_orig_df['depabgled'] > 0,
                          ['ccode1', 'ccode2', 'depbagled', 'year']]
edge_rev_df[['ccode1', 'ccode2']] = edge_rev_df[['ccode2', 'ccode1']]
edge_rev_df['weight'] = edge_rev_df['depbagled']
del edge_rev_df['depbagled']

edge_df = pd.concat([edge_df, edge_rev_df])
edge_df = edge_df[pd.notnull(edge_df['weight'])]
del edge_rev_df
del edge_orig_df

#%% Get nodes
node_df = pd.read_csv(data_dir + 'states2016.csv')
# The same ccode can be used twice to identify the 'same' country in
# different years, so only take later states.
node_df = node_df[node_df['endyear'] >= edge_df['year'].min()];

#%% Create graph
G = ig.Graph.DictList(
        vertices=node_df.to_dict('records'),
        edges=edge_df.to_dict('records'),
        vertex_name_attr='ccode',
        edge_foreign_keys=('ccode1', 'ccode2'),
        directed=True)

print('Network has {0} nodes and {1} edges.'.format(G.vcount(), G.ecount()))
del edge_df
del node_df

#%% Create multislice graph
years = [int(y) for y in set(G.es['year'])]
G_t = []
for year in years:
  H = G.subgraph_edges(G.es.select(year_eq = year), delete_vertices=False)
  H.delete_vertices(H.vs.select(styear_gt = year))
  H.delete_vertices(H.vs.select(endyear_lt = year))
  H['year'] = year
  H['t'] = year - min(years)
  H.vs['year'] = H['year']
  H.vs['t'] = H['t']
  G_t.append(H)

#%% Calculate maxflow
print('\nCalculating maxflow...')
maxflows = [];
for year, H in zip(years, G_t):
  print('\tCalculating maxflow for {0}'.format(year))
  maxflow = [(s['ccode'], t['ccode'], year, 
              H.maxflow_value(s.index, t.index, capacity='weight')) 
              for s in H.vs
                for t in H.vs
              if s != t]
  maxflows.extend(maxflow)

#%% Write maxflow to file
maxflow_df = pd.DataFrame(maxflows, columns=['source_ccode', 'target_ccode', 'year', 'maxflow'])
maxflow_df.to_csv(output_dir + 'maxflow.csv', index=False)

#%% Set seed for random number generator
louvain.set_rng_seed(0)

#%% Covert slices to layers
interslice_weight = 0;
G_intraslice, G_interslice, G_all = louvain.time_slices_to_layers(G_t, 
                                                    interslice_weight=interslice_weight,
                                                    slice_attr='t',
                                                    vertex_id_attr='ccode')


#%% Do community detection
print('\nDoing community detection...')
n_repl = 100
resolutions = [0.6, 1.1, 1.7]
for resolution in resolutions:
    memberships = []
    print('Detecting communities using resolution parameter {0}'.format(resolution))
    for itr in range(n_repl):
      print('\tRun {0:02d}'.format(itr))

      partition_intraslice = [louvain.RBConfigurationVertexPartition(H, weights='weight',
                                                resolution_parameter=resolution)
                              for H in G_intraslice]
      partition_interslice = louvain.CPMVertexPartition(G_interslice,
                                                        weights='weight',
                                                        node_sizes=G_interslice.vs['node_size'], 
                                                        resolution_parameter=0)
      
      ##%% Optimise partitions
      opt = louvain.Optimiser()
      opt.consider_comms = louvain.ALL_NEIGH_COMMS
      opt.optimise_partition_multiplex(partition_intraslice + [partition_interslice])

      # The membership in all partitions will be identical, so simply
      # consider the membership for the interslice partition and graph.
      memberships.append(partition_interslice.membership)
    
    ##%% Write results to file
    cluster_df = pd.DataFrame({attr: G_interslice.vs[attr] for attr in 
                               G_interslice.vertex_attributes()}, index=[v.index for v in G_interslice.vs])
    membership_df = pd.DataFrame.from_records(zip(*memberships), columns=['run_{0}'.format(itr) for itr in range(n_repl)]);
    cluster_df = pd.concat([cluster_df, membership_df], axis=1)
    cluster_df = cluster_df.sort_values(['statenme', 'year'])
    cluster_df.to_csv(output_dir + 'comms_{0}.csv'.format(resolution), index=False)

    ##%% Calculate pairwise same community variable
    run_cols = list(membership_df.columns)
    all_cols = run_cols + ['ccode', 'year']
    # Look at all ccode combinations per year
    pairs_df = pd.merge(cluster_df[all_cols], cluster_df[all_cols], on='year')
    # Only consider pairs that are different
    pairs_df = pairs_df[pairs_df['ccode_x'] != pairs_df['ccode_y']]
    # Consider pairs in the same comm if clustered together at least 50% of the time
    pairs_df['same_comm'] = np.sum(pairs_df[[col + '_x' for col in run_cols]].values == pairs_df[[col + '_y' for col in run_cols]].values, axis=1) >= 0.5*membership_df.shape[1]
    # Only keep the ccode pairs for each year and the same comm variable.
    pairs_df = pairs_df[['ccode_x', 'ccode_y', 'year', 'same_comm']]
    # Write to file
    pairs_df.to_csv(output_dir + 'dyads_{0}.csv'.format(resolution), index=False)
