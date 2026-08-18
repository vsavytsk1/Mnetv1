// WITNESS 6 -- C#.
//
//   chi(T) = 20T - 30T + (10T + 2) = 2, for every T.
//
// Compiled with the C# compiler that SHIPS WITH WINDOWS:
//   C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
// No SDK, no NuGet, no package restore -- the same zero-dependency rule the
// rest of the cave follows. That compiler is C# 5 era, so this file avoids
// top-level statements and string interpolation on purpose.
//
// `long` is Int64, the same width as Rust's i64, so this witness shares an
// overflow boundary with the Rust ones that Python (arbitrary precision) does
// not have, and that JavaScript (binary64, exact only below 2^53) does not
// share either.
//
// C# is also the language of the VR kernel -- MnetUni/Mnet,
// Assets/Kernel/GoldbergKernel.cs, running on a Quest 3 in binary32. Agreement
// here is agreement with that build's integer arithmetic.

using System;
using System.Text;

class ChiWitness
{
    static long Chi(long t)
    {
        long v = 20 * t;
        long e = 30 * t;
        long f = 10 * t + 2;
        return v - e + f;
    }

    static int Main()
    {
        long[] probes = { 0, 1, 2, 3, 21, 147, 1029, 7203, 50421, 1000000 };
        StringBuilder sb = new StringBuilder("csharp");
        bool ok = true;
        for (int i = 0; i < probes.Length; i++)
        {
            long c = Chi(probes[i]);
            if (c != 2) ok = false;
            sb.Append("|").Append(probes[i]).Append(":").Append(c);
        }
        Console.WriteLine(sb.ToString());
        return ok ? 0 : 1;
    }
}
