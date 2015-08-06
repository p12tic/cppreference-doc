
  Information
  -----------
 
This directory contains dummy C++ standard library that contains only the
declarations of the C++ standard library interface, to be used as an aid in
code completion.

Real standard library implementations often use complex C++ techniques in order 
to provide full compliance and perform optimizations. This leads to code 
completion implementations being unable to resolve typedef result and function 
return types, and thus being unable to provide code completion of class members 
when given instance variable. This issue becomes more and more important with 
widespread use of C++ 'auto' type specifier, because code completion of members
of such variables depend on function return types being correctly resolved.

This dummy library performs various steps to simplify the exposed interface, to
make code completion more useful. In addition to that, descriptive parameter
names are exposed instead of uglified identifiers used in real standard library
implementations. The parameter names correspond to those provided for 
respective functions in the cppreference.com C++ reference.

  Configuration
  -------------

The exposed interface depends on the values of the following preprocessor 
macros:

 - CPPREFERENCE_STDVER: defines the standard version of the interface. Possible
   values are 1998, 2003, 2011, 2014, 2017 which correspond to the respective
   C++ standards.
 
 - CPPREFERENCE_SIMPLIFY_TYPEDEFS: non-zero value results in simplified 
   typedefs being exposed. Usage of various traits is greatly reduced; the 
   typedefs refer to types that would be resolved in most common cases. 
   Enabling this is recommended.

  Usage
  -----

The primary target for this dummy C++ standard library is the Qt Creator IDE, 
though the code might be useful in other IDEs.

For each Qt Creator project, perform the following steps to replace the 
C++ library used by code completion:

 - Add the path to this directory to the $PROJECT.includes file

 - Define CPPREFERENCE_STDVER and/or CPPREFERENCE_SIMPLIFY_TYPEDEFS to correct
   values in the $PROJECT.config file.