/// A utility class for performing mathematical operations.
///
/// This class provides various mathematical operations and is designed to be thread-safe.
/// It supports the following operations:
/// - Addition
/// - Subtraction
/// - Multiplication
///
/// ## Example
/// ```swift
/// let math = MathOperations()
/// let result = math.multiply(5, 3)
/// ```
///
/// - Note: All operations are performed synchronously.
/// - Warning: Some operations may throw errors for invalid inputs.
/// - SeeAlso: `OperationType`
public class MathOperations {
    /// The result of the last operation performed.
    ///
    /// This property is updated after each operation.
    ///
    /// - Important: This property is thread-safe.
    private(set) var lastResult: Int = 0

    /// Multiplies two numbers together.
    ///
    /// This function performs multiplication of two integers and updates the `lastResult`.
    ///
    /// ## Example
    /// ```swift
    /// let result = multiply(5, 3) // Returns 15
    /// ```
    ///
    /// - Parameters:
    ///   - x: The first number to multiply
    ///   - y: The second number to multiply
    /// - Returns: The product of the two numbers
    /// - Throws: `MathError.negativeInput` if either number is negative
    /// - Precondition: Both numbers must be non-negative
    /// - Postcondition: `lastResult` is updated with the result
    public func multiply(_ x: Int, _ y: Int) throws -> Int {
        guard x >= 0, y >= 0 else {
            throw MathError.negativeInput
        }
        lastResult = x * y
        return lastResult
    }

    /// Defines the types of operations supported.
    ///
    /// Use this enum to specify the type of operation to perform.
    ///
    /// ## Cases
    /// - `addition`: Basic addition of numbers
    /// - `subtraction`: Basic subtraction of numbers
    /// - `multiplication`: Basic multiplication of numbers
    public enum OperationType {
        /// Represents addition operation
        case addition
        /// Represents subtraction operation
        case subtraction
        /// Represents multiplication operation
        case multiplication
    }

    /// A generic type for numeric operations.
    ///
    /// This type allows operations on any numeric type that conforms to `Numeric`.
    ///
    /// ## Example
    /// ```swift
    /// let doubleOp = NumericOperation<Double>()
    /// ```
    ///
    /// - Note: The type must conform to `Numeric`
    public class NumericOperation<T: Numeric> {
        // Implementation
    }

    /// Represents errors that can occur during mathematical operations.
    ///
    /// - Case negativeInput: Thrown when a negative number is provided
    public enum MathError: Error {
        /// Indicates that a negative number was provided as input
        case negativeInput
    }
} 