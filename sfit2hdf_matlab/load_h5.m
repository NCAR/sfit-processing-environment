function p = load_h5(h5file, datestart, datestop)
% loads intermediate hdf5 (made by create_h5file.py) file for sfit4 into p structure

datestart = datenum(datestart);
datestop = datenum(datestop);

dates = hdf5read(h5file, '/mdate');

for nr = 1:length(dates)
    % python seems to have different numbering scheme, year - 1 and
    % day - 1  
    dvec = datevec(dates(nr));
    dvec(1) = dvec(1) + 1;
    ddates(nr) = datenum(dvec) + 1;
end 

ind = find(ddates > datestart & ddates < datestop);
for nr = 1:length(ind)
    p{nr}.date = ddates(ind(nr));
end 

t = hdf5read(h5file, '/T');
for nr = 1:length(ind)
    p{nr}.T = t(ind(nr),:)';
end
t = hdf5read(h5file, '/P');
for nr = 1:length(ind)
    p{nr}.P = t(ind(nr),:)';
end
t = hdf5read(h5file, '/Z');
for nr = 1:length(ind)
    p{nr}.Z = t;
end
t = hdf5read(h5file, '/Zb');
for nr = 1:length(ind)
    p{nr}.Zb = t';
end
t = hdf5read(h5file, '/vmr_ap');
for nr = 1:length(ind)
    p{nr}.apriori = t(ind(nr),:)';
end
t = hdf5read(h5file, '/vmr_rt');
for nr = 1:length(ind)
    p{nr}.vmr = t(ind(nr),:)';
end
t = hdf5read(h5file, '/cov_vmr_ran');
for nr = 1:length(ind)
    p{nr}.vmr_ran = squeeze(t(ind(nr),:,:));
end
t = hdf5read(h5file, '/cov_vmr_sys');
for nr = 1:length(ind)
    p{nr}.vmr_sys = squeeze(t(ind(nr),:,:));
end
t = hdf5read(h5file, '/avk_vmr');
for nr = 1:length(ind)
    p{nr}.avk = squeeze(t(ind(nr),:,:));
end
t = hdf5read(h5file, '/avk_col');
for nr = 1:length(ind)
    p{nr}.avk_col = sum(squeeze(t(ind(nr),:,:)),1);
end
t = hdf5read(h5file, '/pcol_rt');
for nr = 1:length(ind)
    p{nr}.vcart = t(ind(nr),:)';
end
t = hdf5read(h5file, '/pcol_ap');
for nr = 1:length(ind)
    p{nr}.vcaap = t(ind(nr),:)';
end
t = hdf5read(h5file, '/sza');
for nr = 1:length(ind)
    p{nr}.sza = t(ind(nr));
end
t = hdf5read(h5file, '/zenith');
for nr = 1:length(ind)
    p{nr}.azi = t(ind(nr));
end
t = hdf5read(h5file, '/lat');
for nr = 1:length(ind)
    p{nr}.latitude = t(ind(nr));
end
t = hdf5read(h5file, '/lon');
for nr = 1:length(ind)
    p{nr}.longitude = t(ind(nr));
end
t = hdf5read(h5file, '/alt');
for nr = 1:length(ind)
    p{nr}.altitude = t(ind(nr));
end
t = hdf5read(h5file, '/iter');
for nr = 1:length(ind)
    p{nr}.iter = t(ind(nr));
end
t = hdf5read(h5file, '/itmx');
for nr = 1:length(ind)
    p{nr}.max_iter = t(ind(nr));
end
t = hdf5read(h5file, '/dur');
for nr = 1:length(ind)
    p{nr}.integration_time = t(ind(nr));
end
t = hdf5read(h5file, '/snr_clc');
for nr = 1:length(ind)
    p{nr}.snr_clc = t(ind(nr));
end
t = hdf5read(h5file, '/snr_the');
for nr = 1:length(ind)
    p{nr}.snr_the = t(ind(nr));
end
t = hdf5read(h5file, '/col_rt');
for nr = 1:length(ind)
    p{nr}.col_rt = t(ind(nr));
end
t = hdf5read(h5file, '/col_ap');
for nr = 1:length(ind)
    p{nr}.col_ap = t(ind(nr));
end
t = hdf5read(h5file, '/col_sys');
for nr = 1:length(ind)
    p{nr}.col_sys = t(ind(nr));
end
t = hdf5read(h5file, '/col_ran');
for nr = 1:length(ind)
    p{nr}.col_ran = t(ind(nr));
end
t = hdf5read(h5file, '/gasnames');
for nr = 1:length(ind)
    s = {};
    p{nr}.target = t(1).Data;
    for nr2 = 2:length(t)
        s{nr2-1} = t(nr2).Data;
    end
    p{nr}.interfering.gases = s;
end
t = hdf5read(h5file, '/ivmr_rt');
for nr = 1:length(ind)
    p{nr}.interfering.vmr = squeeze(t(ind(nr),:,:))';
end
t = hdf5read(h5file, '/icol_rt');
for nr = 1:length(ind)
    p{nr}.interfering.col = squeeze(t(ind(nr),:));
end

