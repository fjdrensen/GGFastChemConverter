import numpy as np
from astropy.io import ascii
from astropy.table import Table

# This code is meant to convert GGchem-formatted Static_Conc.dat files to FastChem formatted output files

# Reading in data
file = 'inputfile.dat'
data = ascii.read(file, header_start = 2, data_start = 3)
header = data.colnames

# Reverse to FastChem order. This is useful if you reversed the order of TP_LOW in GGchem for convergence
#data.reverse()

# Change units of pressure
data['pgas'] = data['pgas']/1e6

# Changing column names to FastChem keys
data.rename_column('Tg', 'Tk')
data.rename_column('nHges', 'n_H')
data.rename_column('pgas', 'Pbar')
data.rename_column('mu/amu', 'mu')
data.rename_column('el', 'e_minus')

# Converting values
t = Table()
rowtotals = np.zeros(len(data))

# Now we need to find where the gas chemistries, supersaturation ratios and condensate chemistries start 
# and end, since this can differ for different input parameters.

# Find index of electrons (from which on we find gas phase columns)
electrons_ind = header.index('el')

# Find condensate indices
condensates = []
for i in range(len(header)):
    if header[i][0] == 'n':
        condensates.append(header[i])

condensates.pop(0) # the first 'n' is nHges, not the 'n' before a condensate so we take that one out

condensates_indices = []
for i in range(len(condensates)):
    condensate_i = condensates[i]
    condensates_indices.append(header.index(condensate_i)) # this is our list of condensate indices

firstsolid = condensates[0][1:] # if we know what the name is of the first solid, we can find the first supersaturation ratio and not confuse it with Sulphur species

# Find supersaturation ratio indices
supsat = []
firstsupsatindex = header.index('S'+firstsolid)

for i in range(len(header)):
    if i >= firstsupsatindex and header[i][0] == 'S':
        supsat.append(header[i])
    
supsat_indices = []
for i in range(len(supsat)):
    supsat_i = supsat[i]
    supsat_indices.append(header.index(supsat_i)) # this is our list of condensate indices   
    
# First convert out of log(10) values for relevant columns
for i in np.arange(len(header)):
    col = data[i][:]
    if i < electrons_ind: # no conversion for Tk, n_H or Pbar
        pass
    if i > (electrons_ind - 1) and i < supsat_indices[0]: # from e_minus to the last species before the supersaturation ratios
        for j in range(len(col)):
            float_value = float(col[j])
            power_value = 10**float_value
            col[j] = power_value
            rowtotals[j] += power_value # adding to total number density for the mixing ratios
    if i > (supsat_indices[-1] - 1) and i < condensates_indices[0]: # no action required for the superstaturation ratios
        pass
    if i > (condensates_indices[-1] - 1) and (i < condensates_indices[-1] + 1): # converting the condensates 
        for j in range(len(col)):
            float_value = float(col[j])
            power_value = 10**float_value
            col[j] = power_value
            rowtotals[j] += power_value # again for the mixing ratios
    if i == (len(header) - 1): # converting mu out of log(10) units. 
        float_value = float(col[j])
        power_value = 10**float_value
        col[j] = power_value

# Converting to mixing ratios, using the total of all number density row sums
for i in range(len(header)):
    col = data[i][:]
    if i < electrons_ind: # Tk, n_H, Pbar
        t.add_column(col)
    if i > (electrons_ind - 1) and i < supsat_indices[0]: # gas species
        for j in range(len(col)):
            col[j] = col[j]/rowtotals[j]
        t.add_column(col)
    if i > (supsat_indices[-1] - 1) and i < condensates_indices[0]: # supersaturation ratios
        pass
    if i > (condensates_indices[-1] - 1) and (i < condensates_indices[-1] + 1): # condensates
        for j in range(len(col)):
            col[j] = col[j]/rowtotals[j]
        t.add_column(col)
    if i == (len(header) - 1):
        t.add_column(col)
    
# Writing out to new file
outputfile = 'outputfile.dat'
ascii.write(t, outputfile, overwrite = True)
