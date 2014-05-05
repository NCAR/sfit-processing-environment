function create_hdf_input(template, defaultmeta, species, p)
% Puts all profile found in p into one hdf file input.
    
    fid = fopen(template);
    fid1 = fopen(defaultmeta);
    fid2 = fopen('data.meta', 'w+');
    fid3 = fopen('data.data', 'w+');
    
    while ~feof(fid1)
        ll= fgetl(fid1);
        if isempty(strfind(ll,'DATA_VARIABLES'))
            ind = strfind(ll, 'XXX');
            if ~isempty(find(ind))
                ll = [ll(1:ind-1) species ll(ind+3:end)];
            end
            fprintf(fid2, '%s\n', ll);
        end
    end
    
    ll = fgetl(fid);
    variables = strread(ll, '%s', 'delimiter', ':');
    variables(end) = [];

    nr_vars = 0;
    
    while ~feof(fid)
        ll = fgetl(fid);
        values = strread(ll, '%s', 'delimiter', ':');

        % Remove " if exists
        for n = 1:length(values)
            if length(values{n}) > 1 & values{n}(1) == '"'
                values{n}([1 end]) = [];
            end
        end
        
        % Set gas
        a = strfind(values{1}, '[GAS]');
        if ~isempty(a)
            values{1}(a:a+5) = [];
            str = values{1};
            values{1} = [species '.' values{1}];
        else
            str = values{1};
        end

        % or use H2O
        a = strfind(values{1}, 'H2O');
        if ~isempty(a)
            species = 'H2O_i';
            str = values{1};
            str(a:a+3) = [];
        end

        nr_vars = nr_vars + 1;
        vars_in_hdf{nr_vars} = values{1}; 
        
        for n = 1:length(variables)            
            fprintf(fid2, '%s = %s\n', variables{n}, values{n});
        end
        fprintf(fid2, '\n');
        
        % Remove variable part (gas)
        a = strfind(str, '.');
        str(a) = '_'; 
        str = sprintf('write_%s(p,species,fid3)', str);
        eval (str);
    end


    fprintf(fid2, 'DATA_VARIABLES=');
    for n=1:nr_vars
        fprintf(fid2, '%s;', vars_in_hdf{n});
    end
    
    
    fclose(fid);
    fclose(fid1);
    fclose(fid2);
    fclose(fid3);

    % Correct DATA_VARIABLES field
    
    

end

function write_LATITUDE_INSTRUMENT(p,species,fid03)
    fprintf(fid03, 'LATITUDE.INSTRUMENT\n');
    fprintf(fid03, '%f\n', p{1}.latitude);
end

function write_LONGITUDE_INSTRUMENT(p,species,fid03) 
    fprintf(fid03, 'LONGITUDE.INSTRUMENT\n');
    fprintf(fid03, '%f\n', p{1}.longitude);
end

function write_ALTITUDE_INSTRUMENT(p,species,fid03) 
    fprintf(fid03, 'ALTITUDE.INSTRUMENT\n');
    fprintf(fid03, '%f\n', p{1}.altitude);
end

function write_DATETIME(p,species,fid03) 
    fprintf(fid03, 'DATETIME\n');
    for n=1:length(p)
        fprintf(fid03, '%f\n', p{n}.date - datenum([2000,1,1]));
    end
end



function write_ALTITUDE(p,species,fid03) 
    fprintf(fid03,'ALTITUDE\n');
    fprintf(fid03, '%f\n', p{1}.Z);
end   

function write_ALTITUDE_BOUNDARIES(p,species,fid03) 
    fprintf(fid03,'ALTITUDE.BOUNDARIES\n');
    fprintf(fid03, '%f\n', p{1}.Zb(:,2));
    fprintf(fid03, '%f\n', p{1}.Zb(:,1));
end   

function write_PRESSURE_INDEPENDENT(p,species,fid03) 
    fprintf(fid03,'PRESSURE_INDEPENDENT\n');
    for n=1:length(p)
        fprintf(fid03, '%f\n', p{n}.P);
    end
end 

function write_SURFACE_PRESSURE_INDEPENDENT(p,species,fid03) 
    fprintf(fid03,'SURFACE.PRESSURE_INDEPENDENT\n');
    for n=1:length(p)
        fprintf(fid03, '%f\n', -90000);
    end
end 

function write_TEMPERATURE_INDEPENDENT(p,species,fid03) 
    fprintf(fid03,'TEMPERATURE_INDEPENDENT\n');
    for n=1:length(p)
        fprintf(fid03, '%f\n', p{n}.T);
    end
end 

function write_SURFACE_TEMPERATURE_INDEPENDENT(p,species,fid03) 
    fprintf(fid03,'SURFACE.TEMPERATURE_INDEPENDENT\n');
    for n=1:length(p)
        fprintf(fid03, '%f\n', -90000);
    end
end 

function write_MIXING_RATIO_VOLUME_ABSORPTION_SOLAR(p,species,fid03)
    if strcmp(species, 'H2O_i')
        species = 'H2O';
        for n=1:length(p)            
            ind = find(strcmp(p{n}.interfering.gases, 'H2O'));
            if isempty(ind)
                vmr(n,:) = -90000*ones(size(p{n}.vmr));
            else
                vmr(n,:) = p{n}.interfering.vmr(:,ind)*1e6;
            end
        end
    else
        for n=1:length(p)
            vmr(n,:) =  p{n}.vmr*1e6;
        end
    end
    fprintf(fid03,'%s.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR\n', species);
    fprintf(fid03, '%20.18f\n', vmr');
end 

function write_MIXING_RATIO_VOLUME_ABSORPTION_SOLAR_APRIORI(p,species,fid03)
    fprintf(fid03,'%s.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_APRIORI\n', species);
    for n=1:length(p)
        fprintf(fid03, '%20.18f\n', p{n}.apriori*1e6);
    end
end 

function write_MIXING_RATIO_VOLUME_ABSORPTION_SOLAR_UNCERTAINTY_RANDOM_COVARIANCE(p,species,fid03)
    fprintf(fid03,'%s.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.vmr_ran);
    end
end 

function write_MIXING_RATIO_VOLUME_ABSORPTION_SOLAR_UNCERTAINTY_SYSTEMATIC(p,species,fid03)
    fprintf(fid03,'%s.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.vmr_sys);
    end
end 

function write_MIXING_RATIO_VOLUME_ABSORPTION_SOLAR_AVK(p,species,fid03)
    fprintf(fid03,'%s.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_AVK\n', species);
    for n=1:length(p)
        for m = 1:size(p{n}.avk,1)
		  fprintf(fid03, '%g\n', p{n}.avk(:,m));
        end
    end
end 

function write_COLUMN_PARTIAL_ABSORPTION_SOLAR(p,species,fid03)
    fprintf(fid03,'%s.COLUMN.PARTIAL_ABSORPTION.SOLAR\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.vcart);
    end
end 

function write_COLUMN_PARTIAL_ABSORPTION_SOLAR_APRIORI(p,species,fid03)
    fprintf(fid03,'%s.COLUMN.PARTIAL_ABSORPTION.SOLAR_APRIORI\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.vcaap);
    end
end 

function write_COLUMN_ABSORPTION_SOLAR(p,species,fid03)
    if strcmp(species, 'H2O_i')
        species = 'H2O';
        for n=1:length(p)
            ind = find(strcmp(p{n}.interfering.gases, 'H2O'));
            if isempty(ind)
                col(n) = -90000;
            else
                col(n) = p{n}.interfering.col(ind);
            end
        end
    else
        for n=1:length(p)
            col(n) = p{n}.col_rt;
        end
    end
    fprintf(fid03,'%s.COLUMN_ABSORPTION.SOLAR\n', species);
    fprintf(fid03, '%g\n', col');
end 

function write_COLUMN_ABSORPTION_SOLAR_APRIORI(p,species,fid03)
    fprintf(fid03,'%s.COLUMN_ABSORPTION.SOLAR_APRIORI\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', sum(p{n}.col_ap));
    end
end 

function write_COLUMN_ABSORPTION_SOLAR_UNCERTAINTY_RANDOM_STANDARD(p,species,fid03)
    fprintf(fid03,'%s.COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.col_ran);
    end
end 

function write_COLUMN_ABSORPTION_SOLAR_UNCERTAINTY_SYSTEMATIC_STANDARD(p,species,fid03)
    fprintf(fid03,'%s.COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.STANDARD\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.col_sys);
    end
end 

function write_COLUMN_ABSORPTION_SOLAR_AVK(p,species,fid03)
    fprintf(fid03,'%s.COLUMN_ABSORPTION.SOLAR_AVK\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.avk_col);
    end
end 

function write_INTEGRATION_TIME(p,species,fid03)
    fprintf(fid03,'INTEGRATION.TIME\n', species);
    for n=1:length(p)
        fprintf(fid03, '%g\n', p{n}.integration_time);
    end
end 

function write_ANGLE_SOLAR_ZENITH_ASTRONOMICAL(p,species,fid03)
    fprintf(fid03,'ANGLE.SOLAR_ZENITH.ASTRONOMICAL\n');
    for n=1:length(p)
        fprintf(fid03,'%f\n', p{n}.sza);
    end
end

function write_ANGLE_SOLAR_AZIMUTH(p,species,fid03)
    fprintf(fid03,'ANGLE.SOLAR_AZIMUTH\n');
    for n=1:length(p)
        fprintf(fid03,'%f\n', p{n}.azi);
    end
end
