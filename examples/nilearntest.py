from nilearn import datasets
from nilearn import plotting

print('Datasets shipped with nilearn are stored in: %r' % datasets.get_data_dirs())

motor_images = datasets.fetch_neurovault_motor_task()
stat_img = motor_images.images[0]
# stat_img is just the name of the file that we downloaded
print('The first image is %r' % stat_img)
plotting.plot_glass_brain(stat_img, threshold=3)
# save the plot
plotting.show()