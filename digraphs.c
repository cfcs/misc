// $ digrap
//   exit 1
// $ digrap a
//   exit 2
// $ digrap ba
//   exit 3

int main(int argc, char**argv)
<%

  if ( 2 == argc && 1<:argv<:1:>:> == 'a' ) <% return 3; %>

%: if 1 == 1
  if ( argv<:1:> ) <% return 2; %>
%: endif


  return 1;
%>
