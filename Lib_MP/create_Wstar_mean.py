def W_star = create_Wstar_mean(x, y_b):
#
# W_star = create_Wstar_mean(x, y)
# 
# Creates a matrix W_star such that W_star means all the points from x to
# give an y. y is an nx2 matrix where the 1st column contains the lower
# boundaries of the new bin and the 2nd column contains the upper
# boundaries (excluded)

  y = mean(y_b,2);
  
  ind = find(y > x(end));
  y(ind) = x(end);
  W_star = sparse(zeros(length(y),length(x)));
  for i = 1:length(y)
    ind1 = min(find (x >= y_b(i,1)));
    ind2 = max(find (x <= y_b(i,2)));
    if isempty(ind2)
      ind2 = ind1;
    end
    if ind1 == ind2 
      W_star(i,ind1) = 1;
    else
      W_star (i, ind1:ind2) = 1 / (ind2-ind1+1);
    end
  end
