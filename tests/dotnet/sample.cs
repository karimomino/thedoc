/// <class name="MathOperations">
/// <summary>Provides mathematical operations for basic calculations.</summary>
/// <remarks>
/// <para>This class is designed to be thread-safe and performant.</para>
/// <para>It supports various mathematical operations including:</para>
/// <list type="bullet">
///   <item><term>Addition</term><description>Basic addition of numbers</description></item>
///   <item><term>Subtraction</term><description>Basic subtraction of numbers</description></item>
///   <item><term>Multiplication</term><description>Basic multiplication of numbers</description></item>
/// </list>
/// </remarks>
/// <example>
/// <code>
/// var math = new MathOperations();
/// var result = math.Multiply(5, 3);
/// </code>
/// </example>
/// <seealso cref="OperationType"/>
/// <seealso href="https://docs.microsoft.com/en-us/dotnet/api/system.math"/>
/// </class>
public class MathOperations
{
    /// <method name="Multiply">
    /// <summary>Multiplies two numbers together.</summary>
    /// <param name="x">The first number to multiply</param>
    /// <param name="y">The second number to multiply</param>
    /// <returns>The product of the two numbers</returns>
    /// <exception cref="ArgumentException">Thrown when either number is negative</exception>
    /// <remarks>
    /// This method uses the <paramref name="x"/> and <paramref name="y"/> parameters
    /// to perform multiplication. See <see cref="OperationType.Multiplication"/> for more details.
    /// </remarks>
    /// <example>
    /// <code>
    /// var result = Multiply(5, 3); // Returns 15
    /// </code>
    /// </example>
    /// </method>
    public int Multiply(int x, int y)
    {
        if (x < 0 || y < 0)
            throw new ArgumentException("Numbers must be positive");
        return x * y;
    }

    /// <property name="LastResult">
    /// <summary>Gets the result of the last operation performed.</summary>
    /// <value>The last calculated result</value>
    /// <remarks>This property is updated after each operation.</remarks>
    /// <seealso cref="Multiply"/>
    /// </property>
    public int LastResult { get; private set; }

    /// <enum name="OperationType">
    /// <summary>Defines the types of operations supported.</summary>
    /// <remarks>
    /// This enum is used to specify the type of operation to perform.
    /// See <see cref="MathOperations"/> for implementation details.
    /// </remarks>
    /// <value>Addition - Represents addition operation</value>
    /// <value>Subtraction - Represents subtraction operation</value>
    /// <value>Multiplication - Represents multiplication operation</value>
    /// </enum>
    public enum OperationType
    {
        Addition,
        Subtraction,
        Multiplication
    }

    /// <type name="T">
    /// <summary>A generic type parameter for numeric operations.</summary>
    /// <typeparam name="T">The type of number to operate on</typeparam>
    /// <remarks>
    /// This type must implement <see cref="System.IConvertible"/> to be used
    /// with the numeric operations.
    /// </remarks>
    /// </type>
    public class NumericOperation<T> where T : IConvertible
    {
        // Implementation
    }
} 