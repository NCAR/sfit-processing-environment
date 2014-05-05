function make_bunch_hdf(p, location)
% make hdf file for one month each
        
    IDL = '/usr/local/bin/idl'
        
    if strcmpi(p{1}.target, 'HCL')
        p{1}.target = 'HCl'
    end
    
    species = p{1}.target;

    
    hdf_v5 = 0;
    monthly = 1;

    headerfile = sprintf('data.meta');
    datafile   = 'data.data';
    defaultmeta = sprintf('default.meta.%s', lower(location));
    tablefile  = 'tableattrvalue_04R007_idl.dat'; 
    if hdf_v5
        hdf_dir = 'hdf_v5';
        cstring = sprintf(['%s <<EOF \n idlcr8hdf, ''%s'', ''%s'', ''%s'', ' ...
                           '''%s'', %s, %s, %s\nEOF'], IDL, headerfile, datafile, tablefile, ...
                          hdf_dir, '/H5', '/AVK', '/LOG');
    
    else
        hdf_dir = 'hdf_v4';
        cstring = sprintf(['%s <<EOF \n idlcr8hdf, ''%s'', ''%s'', ''%s'', ' ...
                           '''%s'', %s, %s\nEOF'], IDL, headerfile, datafile, tablefile, ...
                          hdf_dir, '/AVK', '/LOG');
    end

    dd=[];

    ind = Check_results(p);
    if ~isempty(ind)
        p(ind) = [];
    end
    
    for nr = 1:length(p)
        dd(nr) = p{nr}.date;
    end
   
    dd_vec = datevec(dd);
    dd_vec(:,4:end) = 0;
    if monthly
       dd_vec(:,2) = 1;
    end	   
    dd_vec(:,3) = 1;
    all_months = datenum(dd_vec);    
    all_months2 = unique(all_months);
    
    for month = all_months2'
        all_in_month = find(month == all_months);
                      disp(sprintf('%d in %s', length(all_in_month), datestr(month)))
        if ~isempty(all_in_month) & length(all_in_month) > 0
            create_hdf_input('template.FTIR.csv',defaultmeta, species, ...
                             p(all_in_month))
            unix(cstring);
        end
    end
    
    
