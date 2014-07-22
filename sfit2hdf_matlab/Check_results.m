function fail1 = Check_results(p)


  vmr_min = -1.0;
    vmr_max = -1.0;
    snr_the_min = -1.0;
    snr_clc_min = -1.0;
    dofs_min = -1.0;
    snr_rat_min = -1;
    snr_rat_max = -1;
    sza_max = -1;
    max_iter = -1;
    chi_2_y = -1
    species = p{1}.target;
    if strcmp(species, 'C2H6')
      dofs_min = 0.8;
      vmr_min = -0.01e-6;
    end
    if strcmp(species, 'HCN')
        snr_the_min = 0;
        snr_clc_min = 50;
        dofs_min = 2.0;
        snr_rat_min = 0.8;
        vmr_min = 0.0;
    end
    if strcmp(species, 'HCl')
        snr_the_min = 0;
        snr_clc_min = 50;
        dofs_min = 2.0;
        snr_rat_min = 0.8;
        vmr_min = 0.0;
    end
    if 0 && strcmp(species, 'O3')
        snr_the_min = 40;
        snr_clc_min = 50;
        sza_max = 85;
        dofs_min = 3.0;
        snr_rat_min = 0.05 % 0.75;
        snr_rat_max = 0.0 % 1.5;
        vmr_min = -1;
        vmr_max = -1; %8e-6;
	chi_2_y = 10;
    end
    if strcmp(species, 'CO')
        snr_the_min = 100;
        sza_max = 85;
        dofs_min = 1.0;
        snr_rat_min = 0.2;
        snr_clc_min = 10;
        vmr_min = -1;
%        vmr_max = 300e-6
    end
    if strcmp(species, 'CH4')
        snr_the_min = 100;
        snr_clc_min = 150;
        sza_max = 85;
        dofs_min = 1.0;
        snr_rat_min = 0.15;
        vmr_min = -1;
        max_iter = 8;
    end
    
    fail1 = [];
    
    for n = 1:length(p)
        % not converged
%        if p{n}.iter > p{n}.max_iter 
%            fail1 = [fail1 n];
%        end
        if max_iter > 0 && p{n}.iter > max_iter
            fail1 = [fail1 n];
        end            
        % no high resolution spectra
        %        if (length(p{n}.nu{1}) > 2) && (p{n}.nu{1}(2) - p{n}.nu{1}(1) > 0.005)
        %    fail1 = [fail1 n];
        %end
        % SZA to high (> 85)
        if sza_max > 0 & p{n}.sza > sza_max
            fail1 = [fail1 n];
        end
        if trace(p{n}.avk) < dofs_min
            fail1 = [fail1 n];
        end
        % smaller than VMR min anywhere?
        if ~isempty(find(p{n}.vmr < vmr_min))
            fail1 = [fail1 n];
        end
        % VMR max anywhere?
        if vmr_max >= 0 && ~isempty(find(p{n}.vmr > vmr_max))
            fail1 = [fail1 n];
        end
        % Water negative?
        ind = find(strcmp(p{n}.interfering.gases, 'H2O'));
        if ~isempty(ind) && p{n}.interfering.col(ind) < 0
            fail1 = [fail1 n];
        end
        snr_rat(n) = mean(p{n}.snr_clc)/p{n}.snr_the;
        snr_the(n) = p{n}.snr_the;
        snr_clc(n) = mean(p{n}.snr_clc);
    end
    
    
    if snr_the_min > 0
        ind = find (snr_the < snr_the_min);
        fail1 = [fail1 ind];
    end

    if snr_rat_min > 0
        ind = find (snr_rat < snr_rat_min);
        fail1 = [fail1 ind];
    end

    if snr_rat_max > 0
        ind = find (snr_rat > snr_rat_max);
        fail1 = [fail1 ind];
    end

    if snr_clc_min > 0
        ind = find (snr_clc < snr_clc_min);
        fail1 = [fail1 ind];
    end
    
    fail1 = unique(fail1);
