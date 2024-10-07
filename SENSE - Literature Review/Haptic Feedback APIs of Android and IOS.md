
## Questions Answered

1. Availability of haptics through a web-browser
2. Capabilities of the native haptic API

---

# Android

- [Android Haptic Samplers Github](https://github.com/android/platform-samples/tree/main/samples/user-interface/haptics)

Has some simple API bindings to provide feedback using pre-defined configs [source](https://developer.android.com/develop/ui/views/haptics/haptic-feedback)

```kotlin
class HapticTouchListener : View.OnTouchListener {
  override fun onTouch(View view, MotionEvent event) : Boolean {
    when (event.actionMasked) {
      MotionEvent.ACTION_DOWN ->
        view.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY)
      MotionEvent.ACTION_UP ->
        view.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY_RELEASE)
    }
    return true
  }
}
```

## Actuators Primer

![Actuator](https://developer.android.com/static/develop/ui/views/haptics/images/lra-overview.svg)

- Has an API for custom waveforms; [source](https://developer.android.com/develop/ui/views/haptics/actuators)

```kotlin
val timings: LongArray = longArrayOf(50, 50, 50, 50, 50, 100, 350, 250)
val amplitudes: IntArray = intArrayOf(77, 79, 84, 99, 143, 255, 0, 255)
val repeatIndex = -1 // Do not repeat.

vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, repeatIndex))
```

>It follows that creating a haptic effect on an Android device requires more than providing a frequency and amplitude value. It is not a trivial task to design a haptic effect from scratch without full access to the engineering specifications of the vibration actuator and the driver.

- Has an API to create custom feedback using Haptic primitives; [source](https://developer.android.com/develop/ui/views/haptics/custom-haptic-effects#vibration_compositions)

```kotlin
vibrator.vibrate(
    VibrationEffect.startComposition().addPrimitive(
      VibrationEffect.Composition.PRIMITIVE_SLOW_RISE
    ).addPrimitive(
      VibrationEffect.Composition.PRIMITIVE_CLICK
    ).compose()
  )
```

## Challenge

- There are 1300 brands and over 24,000 android phones, it is difficult to provide a consistent haptic feedback experience on android as every manufacturer uses different components.

---

# IOS & Apple ecosystem

- Apple workshop on practicing audio haptic design [WWDC21](https://developer.apple.com/videos/play/wwdc2021/10278/)
- Custom Haptic Patterns from a file [docs](https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file)


# React-native

- Supports  a simple vibration API
- Does not support any of the construct your own haptic feedback primitives.

---

# Comparison

React-native doesn't have support for advanced functions in both platforms, presumably due to significant differences in how the advanced APIs are handled, and potentially the more granular control of the apple api.

As mentioned before, the apple api seems to provide greater customizability compared to android, although the efficacy has not been tested by group members.

Android haptics are also constrained due to the large number of distinct devices that need to be supported.