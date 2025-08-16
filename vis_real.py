import zarr
import plotly.graph_objects as go

label_dataset_path = "/home/alien/Research/xskill/experiment/pretrain/2025-08-05_rh20t_1-8/ckpt_299/prototype.zarr"
label_dataset = zarr.open(label_dataset_path)
label_dataset.tree()

def plot_prototype(task,embodiment,eps,prototype_form="softmax_prototypes"):
    if embodiment=='human':
        # task = 'human_'+ task #backup
        task =  task+'_human'
    task_data = label_dataset[f'{embodiment}/{task}']
    eps_end_index = task_data['eps_end'][eps]
    eps_start_index = task_data['eps_end'][eps-1] if eps>1 else 0
    plot_data = task_data[prototype_form][eps_start_index:eps_end_index]
    D = plot_data.shape[1]
    print(plot_data.shape)
    fig = go.Figure()
    for d in range(D):
        fig.add_trace(go.Scatter(
            y=plot_data[:, d],
            mode='lines',
            name=f'Proto {d}'
        ))
    
    fig.update_layout(title="prototype plot",
                      xaxis_title="Time",
                      yaxis_title=f"{prototype_form}",
                      showlegend=True)
    
    fig.show()

# back up
# plot_prototype("draw_light_oven","human",7)
# plot_prototype("draw_light_oven","robot",7)
# back up

# plot_prototype("oven_draw_cloth","human",4)
# plot_prototype("oven_light_cloth","robot",4)

plot_prototype("task_0001","human",4)
plot_prototype("task_0001","robot",4)