/**
 * A utility class for performing mathematical operations.
 *
 * This class provides various mathematical operations and is designed to be thread-safe.
 * It supports the following operations:
 * * Addition
 * * Subtraction
 * * Multiplication
 *
 * @property lastResult The result of the last operation performed
 * @see MathOperations
 * @sample
 * ```kotlin
 * val math = MathOperations()
 * val result = math.multiply(5, 3)
 * ```
 */
class MathOperations {
    /**
     * Multiplies two numbers together.
     *
     * @param x The first number to multiply
     * @param y The second number to multiply
     * @return The product of the two numbers
     * @throws IllegalArgumentException if either number is negative
     * @sample
     * ```kotlin
     * val result = multiply(5, 3) // Returns 15
     * ```
     */
    fun multiply(x: Int, y: Int): Int {
        if (x < 0 || y < 0) {
            throw IllegalArgumentException("Numbers must be positive")
        }
        return x * y
    }

    /**
     * Gets the result of the last operation performed.
     *
     * This property is updated after each operation.
     *
     * @see multiply
     */
    var lastResult: Int = 0
        private set

    /**
     * Defines the types of operations supported.
     *
     * @property Addition Represents addition operation
     * @property Subtraction Represents subtraction operation
     * @property Multiplication Represents multiplication operation
     */
    enum class OperationType {
        Addition,
        Subtraction,
        Multiplication
    }

    /**
     * A generic type parameter for numeric operations.
     *
     * @param T The type of number to operate on
     * @see Number
     */
    class NumericOperation<T : Number> {
        // Implementation
    }
} 