import plotly.graph_objects as go
import plotly.express as px

def update_line_chart(fig):
    # add minor ticks and grid
    fig.update_xaxes(minor_ticks='inside', showgrid=True)
    # highlight yaxis at 0
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightPink')
    # connect gaps
    fig.update_traces(connectgaps=True)
    
def gen_heatmap(corr_matrix, title):
    heatmap = px.imshow(corr_matrix, 
                        title=title,
                        text_auto='.2f',
                        aspect='auto',
                        color_continuous_scale='Rdbu_r',
                        labels={'color': 'corr coeff'},
                        range_color=[-1, 1],)
    heatmap.update_layout(
        coloraxis_colorbar=dict(
            title="R",
        ),
    )
    return heatmap