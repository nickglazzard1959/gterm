import math

def tick_step( data_range, max_ticks ):
    step_table = [10, 5, 2, 1]
    minimum_step = float(data_range) / max_ticks
    magnitude = 10 ** math.floor( math.log( minimum_step, 10 ) + 1e-9 )
    residual = minimum_step / magnitude
    tick_size = magnitude
    for i in range(1,len(step_table)):
        if residual > step_table[i]:
            return step_table[i-1] * magnitude
    return magnitude

def tick_values( data_min, data_max, max_ticks ):
    if( abs(data_min - data_max)  < 1e-9 ):
        return []
    else:
        if data_min > data_max:
            t = data_min
            data_min = data_max
            data_max = t
        data_range = data_max - data_min
        step = tick_step( data_range, max_ticks )
        istep_min = int(math.floor( data_min / step ))
        istep_max = int(math.ceil( data_max / step )) + 1
        values = []
        for i in range(istep_min, istep_max):
            values.append( i * step )
        return values
    
def tick_labels( tick_vals ):
    def trail_0_suppress( valstr ):
        if valstr[-1] == '0':
            return valstr[:-1]
        else:
            return valstr
    #
    maxvalue = max( abs( tick_vals[0] ), abs( tick_vals[-1] ) )
    magnitude = 10 ** math.floor( math.log( maxvalue, 10 ) + 1e-9 )
    labels = []
    scale_label = ''
    if( magnitude < 0.1 or magnitude > 10.0 ):
        scale_label = 'x 10^'+str( int( math.floor( math.log( magnitude, 10 ) + 1e-9 ) ) )
        for tick_val in tick_vals:
            labels.append( trail_0_suppress('{0:.2f}'.format( tick_val / magnitude )) )
    else:
        for tick_val in tick_vals:
            labels.append( trail_0_suppress('{0:.2f}'.format( tick_val )) )
    return (labels, scale_label)

